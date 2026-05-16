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
"""Verify expenses merchants against Wikidata public database.

Usage:
    python3 verify_vendors.py --workspace ./workspace

Output:
    {workspace}/vendor_verification_report.md
    {workspace}/vendor_verification_data.json
"""

import argparse
import csv
import json
import os
import urllib.parse
import urllib.request


def load_unique_vendors(workspace):
    """Load unique vendors from reconciliation_data.json or expenses.csv."""
    recon_path = os.path.join(workspace, "reconciliation_data.json")
    vendors = set()

    # Try reconciliation_data.json first
    if os.path.exists(recon_path):
        try:
            print("Loading unique vendors from reconciliation_data.json...")
            with open(recon_path, "r") as f:
                data = json.load(f)
            for exp in data.get("expenses", []):
                merchant = exp.get("merchant")
                if merchant:
                    vendors.add(merchant.strip())
            # Also grab from invoices if they are unmatched
            for inv in data.get("invoices", []):
                merchant = inv.get("merchant_name")
                if merchant:
                    vendors.add(merchant.strip())
            return sorted(list(vendors))
        except Exception as e:
            print(f"⚠️  Failed to load reconciliation_data.json: {e}")

    # Fall back to expenses.csv
    csv_path = os.path.join(workspace, "expenses.csv")
    if not os.path.exists(csv_path):
        print(f"❌ No expense or reconciliation data found in {workspace}")
        return []

    print("Loading unique vendors from expenses.csv...")
    try:
        with open(csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                merchant = row.get("merchant")
                if merchant:
                    vendors.add(merchant.strip())
    except Exception as e:
        print(f"❌ Failed to load expenses.csv: {e}")

    return sorted(list(vendors))


def verify_vendor(vendor_name):
    """Query Wikidata API to verify if the vendor is a registered business entity."""
    print(f"  Verifying: '{vendor_name}'...")
    
    # URL encode search query
    query_encoded = urllib.parse.quote(vendor_name)
    url = (
        f"https://www.wikidata.org/w/api.php?action=wbsearchentities"
        f"&search={query_encoded}&language=en&format=json"
    )

    # Comply with Wikidata's User-Agent policy
    headers = {
        "User-Agent": "DocumentProcessorVendorVerifier/1.0 (google-managed-agents-templates; ptruiz@google.com)"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode())
            search_results = res_data.get("search", [])
            
            if search_results:
                # Take first result (highest relevance match)
                first_match = search_results[0]
                entity_id = first_match.get("id")
                description = first_match.get("description", "No description available on Wikidata.")
                concept_uri = first_match.get("concepturi")
                label = first_match.get("label")
                
                print(f"    ✅ MATCH: {label} ({entity_id}) — {description}")
                return {
                    "status": "Verified",
                    "id": entity_id,
                    "label": label,
                    "description": description,
                    "uri": concept_uri,
                    "details": f"Found Wikidata entity: [{label}]({concept_uri}) — {description}"
                }
            
            print("    ⚠️  NO MATCH")
            return {
                "status": "Unverified",
                "id": None,
                "label": vendor_name,
                "description": None,
                "uri": None,
                "details": "No matching business entity found in Wikidata. Requires manual or search investigation."
            }
    except Exception as e:
        print(f"    ❌ Error querying Wikidata: {e}")
        return {
            "status": "Error",
            "id": None,
            "label": vendor_name,
            "description": None,
            "uri": None,
            "details": f"Failed to verify via Wikidata: {e}"
        }


def write_outputs(workspace, results):
    """Write verification markdown report and JSON data."""
    report_path = os.path.join(workspace, "vendor_verification_report.md")
    data_path = os.path.join(workspace, "vendor_verification_data.json")

    # Generate Report Markdown
    total = len(results)
    verified_count = sum(1 for r in results.values() if r["status"] == "Verified")
    unverified_count = sum(1 for r in results.values() if r["status"] == "Unverified")
    error_count = sum(1 for r in results.values() if r["status"] == "Error")

    lines = ["# Vendor Verification Report\n"]
    lines.append("## Summary\n")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Unique Vendors | {total} |")
    lines.append(f"| Verified (Wikidata) | {verified_count} |")
    lines.append(f"| Unverified | {unverified_count} |")
    if error_count > 0:
        lines.append(f"| Errors | {error_count} |")
    lines.append("")

    lines.append("## Verification Details\n")
    lines.append("| Vendor Name | Status | Wikidata Entity | Description / Findings |")
    lines.append("|-------------|--------|-----------------|------------------------|")
    for name, r in results.items():
        status_cell = f"**{r['status']}**" if r['status'] == 'Verified' else f"*{r['status']}*"
        entity_cell = f"[{r['id']}]({r['uri']})" if r['uri'] else "—"
        desc = r['description'] if r['description'] else r['details']
        lines.append(f"| {name} | {status_cell} | {entity_cell} | {desc} |")
    lines.append("")

    if unverified_count > 0:
        lines.append("## Unverified Vendors Requiring Research\n")
        lines.append("The following vendors were not found in Wikidata. If these are small local merchants, they are likely legitimate but lack global records. However, they should be researched online to confirm they are not shell companies or fraudulent entries:\n")
        for name, r in results.items():
            if r['status'] == 'Unverified':
                lines.append(f"- **{name}**")
        lines.append("")

    with open(report_path, "w") as f:
        f.write("\n".join(lines))
    print(f"✅ Report saved to {report_path}")

    # Generate JSON Data
    with open(data_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Data saved to {data_path}")


def main():
    parser = argparse.ArgumentParser(description="Verify vendors using Wikidata")
    parser.add_argument("--workspace", default=".agents/workspace", help="Workspace directory")
    args = parser.parse_args()

    print("=== Document Processor: Vendor Verification ===\n")

    vendors = load_unique_vendors(args.workspace)
    if not vendors:
        print("❌ No unique vendors found. Exiting.")
        return

    print(f"Found {len(vendors)} unique vendors to verify\n")

    results = {}
    for vendor in vendors:
        results[vendor] = verify_vendor(vendor)

    print("\nWriting outputs...")
    write_outputs(args.workspace, results)
    print("\n✅ Vendor verification complete!")


if __name__ == "__main__":
    main()
