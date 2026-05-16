#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Extract structured records from invoice files using pypdf and Gemini.

Usage:
    python3 parse_invoices.py --workspace ./workspace

Requires:
    pip install google-genai pypdf

Output:
    {workspace}/parsed_invoices.json
"""

import argparse
import json
import os
import time
import warnings
from google import genai

# Suppress experimental warnings from SDK
warnings.filterwarnings("ignore", message="Interactions usage is experimental")

INVOICE_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg")

EXTRACTION_PROMPT = """Analyze this invoice document and extract the following fields.
Return ONLY a valid JSON object with these keys:
- "date": the invoice date (string, any format found on the document)
- "merchant_name": the vendor or merchant name
- "amount": the total amount as a number (float, no currency symbols)
- "invoice_number": the invoice or reference number (string, or null if not found)

Return ONLY the JSON object. Do NOT wrap it in markdown code blocks."""

EXTRACTION_FROM_TEXT_PROMPT = """Analyze the following text extracted from an invoice and extract these fields.
Return ONLY a valid JSON object with these keys:
- "date": the invoice date (string, any format found on the document)
- "merchant_name": the vendor or merchant name
- "amount": the total amount as a number (float, no currency symbols)
- "invoice_number": the invoice or reference number (string, or null if not found)

Invoice Text:
{text}

Return ONLY the JSON object. Do NOT wrap it in markdown code blocks."""


def find_invoices(workspace):
    """Scan workspace for invoice files."""
    invoice_files = []
    search_dirs = [workspace]

    invoices_dir = os.path.join(workspace, "invoices")
    if os.path.isdir(invoices_dir):
        search_dirs.append(invoices_dir)

    for search_dir in search_dirs:
        for fname in os.listdir(search_dir):
            if fname.lower().endswith(INVOICE_EXTENSIONS):
                invoice_files.append(os.path.join(search_dir, fname))

    return sorted(invoice_files)


def extract_pypdf(pdf_path):
    """Locally extract text from PDF using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"    ⚠️  pypdf extraction failed for {os.path.basename(pdf_path)}: {e}")
        return ""


def clean_response(text):
    """Clean up potential markdown wrapping (e.g. ```json ... ```)."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def extract_gemini_text(client, text):
    """Extract structured data from raw text using Gemini Interactions API."""
    prompt = EXTRACTION_FROM_TEXT_PROMPT.format(text=text)
    
    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input=prompt,
    )
    
    response_text = ""
    if hasattr(interaction, "steps") and interaction.steps and interaction.steps[-1].content:
        response_text = interaction.steps[-1].content[0].text
        
    cleaned_json = clean_response(response_text)
    data = json.loads(cleaned_json)
    
    # Normalize amount to float
    if data.get("amount") is not None:
        try:
            data["amount"] = float(data["amount"])
        except (ValueError, TypeError):
            data["amount"] = 0.0
            
    return data


def extract_gemini_vision(client, file_path, mime_type, input_type):
    """Upload document and extract structured data visually using Gemini API."""
    # 1. Upload file using Files API
    uploaded_file = client.files.upload(file=file_path)
    print(f"    Uploaded as {uploaded_file.name}")
    
    # 2. Extract data via Interactions API
    interaction = client.interactions.create(
        model="gemini-3-flash-preview",
        input=[
            {"type": "text", "text": EXTRACTION_PROMPT},
            {"type": input_type, "uri": uploaded_file.uri, "mime_type": mime_type},
        ],
    )
    
    response_text = ""
    if hasattr(interaction, "steps") and interaction.steps and interaction.steps[-1].content:
        response_text = interaction.steps[-1].content[0].text
        
    cleaned_json = clean_response(response_text)
    data = json.loads(cleaned_json)
    
    # Normalize amount to float
    if data.get("amount") is not None:
        try:
            data["amount"] = float(data["amount"])
        except (ValueError, TypeError):
            data["amount"] = 0.0
            
    return data


def extract_invoice_data(client, invoice_path):
    """Extract structured data from invoice, utilizing local pypdf for PDFs where possible."""
    print(f"  Processing invoice: {os.path.basename(invoice_path)}...")

    ext = os.path.splitext(invoice_path)[1].lower()

    # Try local text extraction if it's a PDF
    if ext == ".pdf":
        print("    Attempting local text extraction with pypdf...")
        pdf_text = extract_pypdf(invoice_path)
        if pdf_text and len(pdf_text) > 10:
            print(f"    ✅ Local text extracted ({len(pdf_text)} chars). Calling Gemini for structured parsing...")
            data = extract_gemini_text(client, pdf_text)
            data["source_file"] = os.path.basename(invoice_path)
            print(f"    ✅ Extracted via text: {data.get('merchant_name', 'Unknown')} — ${data.get('amount', 0):.2f}")
            return data
        else:
            print("    ⚠️  No text extractable from PDF. Falling back to visual Gemini parsing...")

    # Default visual parsing (already implemented)
    type_map = {
        ".pdf": ("application/pdf", "document"),
        ".png": ("image/png", "image"),
        ".jpg": ("image/jpeg", "image"),
        ".jpeg": ("image/jpeg", "image"),
    }
    mime_type, input_type = type_map.get(ext, ("application/octet-stream", "document"))

    data = extract_gemini_vision(client, invoice_path, mime_type, input_type)
    data["source_file"] = os.path.basename(invoice_path)
    print(f"    ✅ Extracted visually: {data.get('merchant_name', 'Unknown')} — ${data.get('amount', 0):.2f}")
    return data


def main():
    parser = argparse.ArgumentParser(description="Parse invoices and extract structured records")
    parser.add_argument("--workspace", default="workspace", help="Workspace directory")
    args = parser.parse_args()

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "dummy-key"))

    print("=== Document Processor: PDF Invoice Parser ===\n")

    invoice_files = find_invoices(args.workspace)
    if not invoice_files:
        print("❌ No invoice files found in workspace.")
        return

    print(f"Found {len(invoice_files)} invoice files to parse\n")

    parsed_records = []
    for inv_path in invoice_files:
        try:
            data = extract_invoice_data(client, inv_path)
            parsed_records.append(data)
        except Exception as e:
            print(f"  ⚠️  Failed to parse {os.path.basename(inv_path)}: {e}")
            time.sleep(1)

    # Write output to parsed_invoices.json
    output_path = os.path.join(args.workspace, "parsed_invoices.json")
    with open(output_path, "w") as f:
        json.dump(parsed_records, f, indent=2)

    print(f"\n✅ Successfully parsed {len(parsed_records)}/{len(invoice_files)} invoices!")
    print(f"✅ Saved database to {output_path}")


if __name__ == "__main__":
    main()
