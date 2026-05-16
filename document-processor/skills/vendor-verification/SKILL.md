---
name: vendor-verification
description: Verify whether vendors/merchants from expense records are real, registered business entities by querying the free Wikidata open API.
---

# Vendor Verification

Verify whether merchants or vendors from expense records are real, registered business entities by querying the free, open **Wikidata API** (no key required). This skill helps identify potentially fraudulent or unverified merchants.

## Embedded Script

```bash
python3 skills/vendor-verification/scripts/verify_vendors.py --workspace .agents/workspace
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--workspace` | `.agents/workspace` | Workspace directory containing expenses.csv or reconciliation_data.json |

### What it does

1. Loads expense records from `.agents/workspace/reconciliation_data.json` (if available from a prior reconciliation run) or directly from `.agents/workspace/expenses.csv`.
2. Identifies all unique vendor/merchant names.
3. For each unique merchant, queries the free **Wikidata Entity Search API**:
   `https://www.wikidata.org/w/api.php?action=wbsearchentities&search={merchant_name}&language=en&format=json`
4. Analyzes the search results:
   - **Verified**: If a matching entity exists on Wikidata. Extracts the description (e.g. *“American multinational technology company”*) and entity ID (e.g., `Q95`).
   - **Unverified**: If no match is found on Wikidata.
5. Generates `.agents/workspace/vendor_verification_report.md` with:
   - Verification summary statistics.
   - A detailed status table for all unique vendors.
   - Flagged unverified vendors requiring secondary research.
6. Generates `.agents/workspace/vendor_verification_data.json` containing the structured JSON results.

### Licensing & Usage

- This skill queries Wikidata, which is licensed under **Creative Commons CC0 1.0 Universal Public Domain Dedication**.
- It is 100% free of charge, requires no API token/key, has no commercial restrictions, and requires no attribution.

## Output

| File | Path | Description |
|------|------|-------------|
| Verification Report | `.agents/workspace/vendor_verification_report.md` | Human-readable markdown report listing verified and unverified merchants with official descriptions. |
| Verification Data | `.agents/workspace/vendor_verification_data.json` | Structured JSON containing merchant verification statuses, descriptions, and Wikidata entity URIs. |
