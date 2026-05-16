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
"""Multimodal data extraction utility using Gemini API.

Usage:
    python3 extract_gemini.py --file ./workspace/invoices/invoice.png
"""

import argparse
import json
import os
import sys
import warnings
from google import genai

# Suppress experimental warnings from SDK
warnings.filterwarnings("ignore", message="Interactions usage is experimental")

EXTRACTION_PROMPT = """Analyze this invoice document and extract the following fields.
Return ONLY a valid JSON object with these keys:
- "date": the invoice date (string, any format found on the document)
- "merchant_name": the vendor or merchant name
- "amount": the total amount as a number (float, no currency symbols)
- "invoice_number": the invoice or reference number (string, or null if not found)

Return ONLY the JSON object. Do NOT wrap it in markdown code blocks."""


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


def extract_gemini_vision(client, file_path, mime_type, input_type):
    """Upload document and extract structured data visually using Gemini API."""
    # 1. Upload file using Files API
    uploaded_file = client.files.upload(file=file_path)
    
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


def main():
    parser = argparse.ArgumentParser(description="Extract structured JSON from invoices using Gemini API")
    parser.add_argument("--file", required=True, help="Path to the invoice file")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found at {args.file}", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "dummy-key"))

    ext = os.path.splitext(args.file)[1].lower()
    type_map = {
        ".pdf": ("application/pdf", "document"),
        ".png": ("image/png", "image"),
        ".jpg": ("image/jpeg", "image"),
        ".jpeg": ("image/jpeg", "image"),
    }
    
    if ext not in type_map:
        print(f"Error: Unsupported file format {ext}", file=sys.stderr)
        sys.exit(1)

    mime_type, input_type = type_map[ext]

    try:
        data = extract_gemini_vision(client, args.file, mime_type, input_type)
        data["source_file"] = os.path.basename(args.file)
        
        # Print JSON output to stdout
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error extracting visually: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
