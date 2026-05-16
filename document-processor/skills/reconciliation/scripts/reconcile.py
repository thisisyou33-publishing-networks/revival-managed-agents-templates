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
"""Reconcile expenses against invoice documents using the Gemini Interactions API.

Usage:
    python3 reconcile.py --workspace ./workspace
    python3 reconcile.py --workspace ./workspace --tolerance 0.50

Requires:
    pip install google-genai

Output:
    {workspace}/reconciliation_report.md
    {workspace}/reconciliation_data.json
"""

import argparse
import csv
import json
import os
import time
from google import genai


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


def load_expenses(csv_path):
    """Load expenses from CSV file."""
    expenses = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["amount"] = float(row.get("amount", 0))
            except (ValueError, TypeError):
                row["amount"] = 0.0
            expenses.append(row)
    return expenses


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


def extract_pdf_text(pdf_path):
    """Extract text from PDF using pypdf."""
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


def extract_invoice_data(client, invoice_path):
    """Extract structured data from invoice, utilizing local pypdf for PDFs where possible."""
    print(f"  Processing invoice: {os.path.basename(invoice_path)}...")

    ext = os.path.splitext(invoice_path)[1].lower()

    # Try local text extraction if it's a PDF
    if ext == ".pdf":
        print("    Attempting local text extraction with pypdf...")
        pdf_text = extract_pdf_text(invoice_path)
        if pdf_text and len(pdf_text) > 10:
            print(f"    ✅ Local text extracted ({len(pdf_text)} chars). Calling Gemini for structured parsing...")
            prompt = EXTRACTION_FROM_TEXT_PROMPT.format(text=pdf_text)
            interaction = client.interactions.create(
                model="gemini-3-flash-preview",
                input=prompt,
            )
            response_text = ""
            if hasattr(interaction, "steps") and interaction.steps and interaction.steps[-1].content:
                response_text = interaction.steps[-1].content[0].text

            # Clean up potential markdown wrapping
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            data = json.loads(response_text)
            if data.get("amount") is not None:
                try:
                    data["amount"] = float(data["amount"])
                except (ValueError, TypeError):
                    data["amount"] = 0.0

            data["source_file"] = os.path.basename(invoice_path)
            print(f"    ✅ Extracted via text: {data.get('merchant_name', 'Unknown')} — ${data.get('amount', 0):.2f}")
            return data
        else:
            print("    ⚠️  No text extractable from PDF. Falling back to visual Gemini parsing...")

    # Default visual parsing (already implemented)
    # Upload file
    uploaded_file = client.files.upload(file=invoice_path)
    print(f"    Uploaded as {uploaded_file.name}")

    # Determine MIME type and input type for Interactions API
    type_map = {
        ".pdf": ("application/pdf", "document"),
        ".png": ("image/png", "image"),
        ".jpg": ("image/jpeg", "image"),
        ".jpeg": ("image/jpeg", "image"),
    }
    mime_type, input_type = type_map.get(ext, ("application/octet-stream", "document"))

    # Extract data via Interactions API
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

    # Clean up potential markdown wrapping
    response_text = response_text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    response_text = response_text.strip()

    data = json.loads(response_text)

    # Normalize amount to float
    if data.get("amount") is not None:
        try:
            data["amount"] = float(data["amount"])
        except (ValueError, TypeError):
            data["amount"] = 0.0

    data["source_file"] = os.path.basename(invoice_path)
    print(f"    ✅ Extracted visually: {data.get('merchant_name', 'Unknown')} — ${data.get('amount', 0):.2f}")
    return data


def normalize_merchant(name):
    """Normalize merchant name for comparison."""
    if not name:
        return ""
    # Remove punctuation and normalize to lowercase
    name = name.lower().strip().replace(",", "").replace(".", "")
    # Remove common business suffixes as whole words only
    words = [w for w in name.split() if w not in ("inc", "llc")]
    return " ".join(words)


def merchants_match(name1, name2):
    """Check if two merchant names are similar enough to match."""
    n1 = normalize_merchant(name1)
    n2 = normalize_merchant(name2)
    if not n1 or not n2:
        return False
    # Exact match after normalization
    if n1 == n2:
        return True
    # Substring match
    if n1 in n2 or n2 in n1:
        return True
    # Word overlap — at least half the words match
    words1 = set(n1.split())
    words2 = set(n2.split())
    if words1 and words2:
        overlap = len(words1 & words2)
        min_len = min(len(words1), len(words2))
        if min_len > 0 and overlap / min_len >= 0.5:
            return True
    return False


def perform_reconciliation(expenses, invoices, tolerance):
    """Match expenses against invoices and identify discrepancies."""
    matched = []
    discrepancies = []
    used_invoices = set()

    for exp_idx, expense in enumerate(expenses):
        best_match = None
        best_match_idx = None
        match_type = None

        for inv_idx, invoice in enumerate(invoices):
            if inv_idx in used_invoices:
                continue

            merchant_ok = merchants_match(expense.get("merchant", ""), invoice.get("merchant_name", ""))
            amount_diff = abs(expense.get("amount", 0) - invoice.get("amount", 0))
            amount_ok = amount_diff <= tolerance

            if merchant_ok and amount_ok:
                best_match = invoice
                best_match_idx = inv_idx
                match_type = "exact"
                break
            elif merchant_ok and not amount_ok:
                if best_match is None:
                    best_match = invoice
                    best_match_idx = inv_idx
                    match_type = "amount_mismatch"
            elif amount_ok and not merchant_ok:
                if best_match is None:
                    best_match = invoice
                    best_match_idx = inv_idx
                    match_type = "merchant_mismatch"

        if best_match and match_type == "exact":
            used_invoices.add(best_match_idx)
            matched.append({
                "expense_index": exp_idx,
                "invoice_index": best_match_idx,
                "expense": expense,
                "invoice": best_match,
            })
        elif best_match and match_type == "amount_mismatch":
            used_invoices.add(best_match_idx)
            diff = abs(expense.get("amount", 0) - best_match.get("amount", 0))
            discrepancies.append({
                "type": "Amount Mismatch",
                "expense": expense,
                "invoice": best_match,
                "details": f"Expense: ${expense.get('amount', 0):.2f}, Invoice: ${best_match.get('amount', 0):.2f} (diff: ${diff:.2f})",
            })
        elif best_match and match_type == "merchant_mismatch":
            used_invoices.add(best_match_idx)
            discrepancies.append({
                "type": "Merchant Mismatch",
                "expense": expense,
                "invoice": best_match,
                "details": f"Expense merchant: '{expense.get('merchant', '')}', Invoice merchant: '{best_match.get('merchant_name', '')}'",
            })
        else:
            discrepancies.append({
                "type": "Missing Invoice",
                "expense": expense,
                "invoice": None,
                "details": f"No invoice found for {expense.get('merchant', 'Unknown')} — ${expense.get('amount', 0):.2f}",
            })

    # Check for unmatched invoices
    for inv_idx, invoice in enumerate(invoices):
        if inv_idx not in used_invoices:
            discrepancies.append({
                "type": "Unmatched Invoice",
                "expense": None,
                "invoice": invoice,
                "details": f"Invoice from {invoice.get('merchant_name', 'Unknown')} — ${invoice.get('amount', 0):.2f} ({invoice.get('source_file', 'unknown')})",
            })

    return matched, discrepancies


def write_report(workspace, expenses, invoices, matched, discrepancies):
    """Write markdown reconciliation report."""
    report_path = os.path.join(workspace, "reconciliation_report.md")

    lines = ["# Reconciliation Report\n"]
    lines.append("## Summary\n")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Expenses | {len(expenses)} |")
    lines.append(f"| Total Invoices | {len(invoices)} |")
    lines.append(f"| Matched | {len(matched)} |")
    lines.append(f"| Discrepancies | {len(discrepancies)} |")
    lines.append("")

    if discrepancies:
        lines.append("## Discrepancies\n")
        lines.append("| Type | Expense Merchant | Invoice Merchant | Details |")
        lines.append("|------|-----------------|------------------|---------|")
        for d in discrepancies:
            exp_merchant = d.get("expense", {}).get("merchant", "—") if d.get("expense") else "—"
            inv_merchant = d.get("invoice", {}).get("merchant_name", "—") if d.get("invoice") else "—"
            lines.append(f"| {d['type']} | {exp_merchant} | {inv_merchant} | {d['details']} |")
        lines.append("")

    if matched:
        lines.append("## Matched Items\n")
        lines.append("| Expense Merchant | Amount | Invoice File |")
        lines.append("|-----------------|--------|--------------|")
        for m in matched:
            merchant = m["expense"].get("merchant", "Unknown")
            amount = m["expense"].get("amount", 0)
            inv_file = m["invoice"].get("source_file", "Unknown")
            lines.append(f"| {merchant} | ${amount:.2f} | {inv_file} |")
        lines.append("")

    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    print(f"✅ Report saved to {report_path}")
    return report_path


def write_data(workspace, expenses, invoices, matched, discrepancies):
    """Write structured JSON reconciliation data."""
    data_path = os.path.join(workspace, "reconciliation_data.json")

    data = {
        "summary": {
            "total_expenses": len(expenses),
            "total_invoices": len(invoices),
            "matched": len(matched),
            "discrepancies": len(discrepancies),
        },
        "expenses": expenses,
        "invoices": invoices,
        "matched": matched,
        "discrepancies": discrepancies,
    }

    with open(data_path, "w") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"✅ Data saved to {data_path}")
    return data_path


def main():
    parser = argparse.ArgumentParser(description="Reconcile expenses against invoices")
    parser.add_argument("--workspace", default="workspace", help="Workspace directory")
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.01,
        help="Amount match tolerance in dollars (default: 0.01)",
    )
    args = parser.parse_args()

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "dummy-key"))

    print("=== Document Processor: Reconciliation ===\n")

    # Load expenses
    csv_path = os.path.join(args.workspace, "expenses.csv")
    if not os.path.exists(csv_path):
        print(f"❌ Expenses file not found at {csv_path}")
        return

    expenses = load_expenses(csv_path)
    print(f"Loaded {len(expenses)} expenses from {csv_path}")

    # Find invoices
    invoice_files = find_invoices(args.workspace)
    if not invoice_files:
        print("⚠️  No invoice files found in workspace.")
        print("   All expenses will be flagged as Missing Invoice.\n")

    print(f"Found {len(invoice_files)} invoice files\n")

    # Extract invoice data
    invoices = []
    for inv_path in invoice_files:
        try:
            data = extract_invoice_data(client, inv_path)
            invoices.append(data)
        except Exception as e:
            print(f"  ⚠️  Failed to process {os.path.basename(inv_path)}: {e}")
            time.sleep(1)

    print(f"\nSuccessfully extracted data from {len(invoices)}/{len(invoice_files)} invoices\n")

    # Perform reconciliation
    print("Performing reconciliation...")
    matched, discrepancies = perform_reconciliation(expenses, invoices, args.tolerance)

    print(f"  Matched: {len(matched)}")
    print(f"  Discrepancies: {len(discrepancies)}\n")

    # Write outputs
    write_report(args.workspace, expenses, invoices, matched, discrepancies)
    write_data(args.workspace, expenses, invoices, matched, discrepancies)

    print(f"\n✅ Reconciliation complete!")


if __name__ == "__main__":
    main()
