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
"""Reconcile expense CSV records against a parsed JSON invoices database locally.

Usage:
    python3 reconcile.py --workspace ./workspace
    python3 reconcile.py --workspace ./workspace --tolerance 0.50

Output:
    {workspace}/reconciliation_report.md
    {workspace}/reconciliation_data.json
"""

import argparse
import csv
import json
import os


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


def load_parsed_invoices(json_path):
    """Load pre-parsed invoices database."""
    if not os.path.exists(json_path):
        print(f"⚠️  No parsed invoices database found at {json_path}")
        return []
    
    with open(json_path, "r") as f:
        return json.load(f)


def normalize_merchant(name):
    """Normalize merchant name for comparison."""
    if not name:
        return ""
    name = name.lower().strip().replace(",", "").replace(".", "")
    words = [w for w in name.split() if w not in ("inc", "llc")]
    return " ".join(words)


def merchants_match(name1, name2):
    """Check if two merchant names are similar enough to match."""
    n1 = normalize_merchant(name1)
    n2 = normalize_merchant(name2)
    if not n1 or not n2:
        return False
    if n1 == n2:
        return True
    if n1 in n2 or n2 in n1:
        return True
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
    parser = argparse.ArgumentParser(description="Local reconciliation script")
    parser.add_argument("--workspace", default=".agents/workspace", help="Workspace directory")
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.01,
        help="Amount match tolerance in dollars (default: 0.01)",
    )
    args = parser.parse_args()

    print("=== Document Processor: Local Reconciliation ===\n")

    # Load expenses
    csv_path = os.path.join(args.workspace, "expenses.csv")
    if not os.path.exists(csv_path):
        print(f"❌ Expenses file not found at {csv_path}")
        return

    expenses = load_expenses(csv_path)
    print(f"Loaded {len(expenses)} expenses from {csv_path}")

    # Load pre-parsed invoices
    json_path = os.path.join(args.workspace, "parsed_invoices.json")
    if not os.path.exists(json_path):
        print(f"❌ Parsed invoices database not found at {json_path}")
        print("   Please run the 'pdf-parsing' skill first to generate parsed_invoices.json.\n")
        return

    invoices = load_parsed_invoices(json_path)
    print(f"Loaded {len(invoices)} pre-parsed invoices from {json_path}\n")

    # Perform reconciliation
    print("Performing local reconciliation...")
    matched, discrepancies = perform_reconciliation(expenses, invoices, args.tolerance)

    print(f"  Matched: {len(matched)}")
    print(f"  Discrepancies: {len(discrepancies)}\n")

    # Write outputs
    write_report(args.workspace, expenses, invoices, matched, discrepancies)
    write_data(args.workspace, expenses, invoices, matched, discrepancies)

    print(f"\n✅ Local Reconciliation complete!")


if __name__ == "__main__":
    main()
