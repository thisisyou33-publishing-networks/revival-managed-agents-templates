# Agent Instructions: Reconciliation Agent

## What This Agent Does
This agent performs a reconciliation between expense transactions and invoices in the workspace. It reads a list of expenses from a CSV file and compares them with corresponding invoice documents (PDFs or Images). It flags any discrepancies, such as amount mismatches, merchant mismatches, or missing documents.

## Workspace Paths
The agent operates in the `.agents/workspace/` directory. It expects to find `expenses.csv` and a set of invoice files (PDF or Image) there.

## Rules
- **Scale**: Use Python to load and compare the data.
- **Generality**: The agent must dynamically match expenses to invoices based on common fields (e.g., date, merchant, amount, employee) and handle fuzzy matching if names differ slightly.
- **Discrepancy Detection**: Flag the following types of discrepancies:
  1. **Amount Mismatch**: The amount on the invoice does not match the expense record.
  2. **Missing Invoice**: An expense exists but no matching invoice is found.
  3. **Unmatched Invoice**: An invoice exists but no matching expense record is found.
  4. **Merchant Mismatch**: The merchant name on the invoice differs significantly from the expense record.
- **Report**: Produce a structured report (`.agents/workspace/reconciliation_report.md`) listing all flagged discrepancies with recommendations.

## Workflow
1. **Load Data**: Load `expenses.csv` and list all invoice files in the workspace.
2. **Extract Invoice Data**: Use appropriate libraries or tools to read text from PDFs or Images to extract date, merchant, amount, and invoice number.
3. **Perform Reconciliation**: Compare the two datasets.
4. **Generate Report**: Write the findings to `.agents/workspace/reconciliation_report.md`.
