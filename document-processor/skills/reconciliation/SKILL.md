---
name: reconciliation
description: Reconcile expenses against invoice documents, flagging discrepancies like amount mismatches, missing invoices, and merchant mismatches.
---

# Reconciliation

Reconcile expenses from a CSV file against invoice documents (PDFs and images) using the Gemini API. The skill extracts structured data from invoices, performs fuzzy matching against expense records, and generates a detailed reconciliation report flagging any discrepancies.

## Embedded Script

```bash
python3 skills/reconciliation/scripts/reconcile.py --workspace ./workspace
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--workspace` | `workspace` | Workspace directory containing expenses.csv and invoice files |
| `--tolerance` | `0.01` | Amount match tolerance in dollars |

### What it does

1. Loads `expenses.csv` from `{workspace}/` (columns: date, employee, merchant, category, amount, memo).
2. Scans workspace root and `invoices/` subdirectory for invoice files (`.pdf`, `.png`, `.jpg`, `.jpeg`).
3. Uploads each invoice to the **Gemini Files API**, then calls `interactions.create()` with `gemini-3-flash-preview` to extract structured data (date, merchant name, amount, invoice number).
4. Performs fuzzy matching between expenses and extracted invoice data (normalized merchant names, amount tolerance).
5. Flags discrepancies: Amount Mismatch, Missing Invoice, Unmatched Invoice, Merchant Mismatch.
6. Generates `{workspace}/reconciliation_report.md` with summary stats and discrepancy table.
7. Generates `{workspace}/reconciliation_data.json` with machine-readable results.

### Dependencies

- `google-genai` (>= 2.0.0)

## Discrepancy Types

| Type | Description |
|------|-------------|
| **Amount Mismatch** | Expense and invoice matched by merchant but amounts differ beyond tolerance |
| **Missing Invoice** | Expense record exists with no matching invoice document |
| **Unmatched Invoice** | Invoice document exists with no matching expense record |
| **Merchant Mismatch** | Expense and invoice matched by amount but merchant names differ significantly |

## Output

| File | Path | Description |
|------|------|-------------|
| Reconciliation Report | `{workspace}/reconciliation_report.md` | Human-readable markdown report with summary stats, discrepancy table, and matched items |
| Reconciliation Data | `{workspace}/reconciliation_data.json` | Structured JSON with expenses, invoices, matches, and discrepancies |
