# AGENTS.md — Document Processor

An AI agent that reconciles expense reports against invoice documents, verifies vendor legitimacy, and produces premium interactive HTML slideshow reports. Give it a folder of invoices and an expense log, and it will automatically detect mismatches, analyze spending patterns, and generate high-end executive-level summaries.

## Workspace

All work is performed in the `./workspace` directory. All paths are relative to `./workspace` unless absolute.

## Before You Do Anything

> [!NOTE]
> The platform automatically injects the correct API key at the network level when scripts run.
> The scripts are already configured to use a dummy key to satisfy the SDK, so you do not need to set `GEMINI_API_KEY`.
> You must trust that the process will work and not worry about Gemini authentication.

1. Immediately install required libraries:
   ```bash
   pip install -r /.agents/requirements.txt --break-system-packages
   ```

## Workflow

> [!IMPORTANT]
> **Bias for Action**: Do NOT ask for approval before executing commands, running scripts, or proceeding to the next step. Proceed autonomously unless there is a material ambiguity or a critical decision that strictly requires user input.

> [!TIP]
> **Maximize Speed & Reduce Calls**:
> - Read all necessary `SKILL.md` files (in the /.agents/skills directory) at once using a single bash command (`cat /.agents/skills/*/SKILL.md`).
> - Do not use `list_files` to verify directories, script paths, or output files—trust the documentation and the script success logs.
> - Chain sequential bash commands using `&&` in a single tool call (e.g., `python3 reconcile.py`).

Upon execution, you should:

1. **Reconcile** — use `reconciliation` skill to match expenses in `expenses.csv` against invoice documents (PDFs and images) in the workspace. Extracts data from files using Gemini, performs fuzzy matching, and flags discrepancies.
2. **Generate Slideshow** — use `slide-creator` skill to write a premium, Google-style interactive HTML slideshow presenting the results of the reconciliation and vendor cost analysis (including charts, layout templates, and structured executive insights).
3. **Verify Vendors (Optional)** — if the user explicitly requests to verify merchants, check if vendors are real, or run fraud checks, use the `vendor-verification` skill to look them up on Wikidata's public open database. For any unverified vendors, use your **Google Search** tool to perform live search investigations (confirming if they are real small/local businesses or potentially fraudulent shell entities), reporting your findings in the final summary.

> [!IMPORTANT]
> When providing the final summary to the user, do NOT include markdown links or URLs to the generated files or scripts (e.g. `[reconcile.py](file:///.agents...)`). Just use the plain file name (e.g. `reconcile.py`). If you notice any links in your drafted response, strip them out and replace them with just the file name.

## Architecture

```
User prompt
  ├── 1. python3 /.agents/skills/reconciliation/scripts/reconcile.py --workspace ./workspace
  │       → {workspace}/reconciliation_report.md
  │       → {workspace}/reconciliation_data.json
  ├── 2. Generate premium presentation HTML directly using the `slide-creator` design system
  │       → {workspace}/reports/vendor_slideshow.html
  └── 3. (Optional) python3 /.agents/skills/vendor-verification/scripts/verify_vendors.py --workspace ./workspace
          → {workspace}/vendor_verification_report.md
          → {workspace}/vendor_verification_data.json
```

## API Surface

All Gemini API calls use the **Interactions API** (`client.interactions.create()`), NOT `generateContent`:

| Step | Model | API |
|------|-------|-----|
| Invoice data extraction | `gemini-3-flash-preview` | `interactions.create()` |
| Narrative/slide generation | `gemini-3-flash-preview` | `interactions.create()` |

## Skills

Each skill lives in `/.agents/skills/<name>/` with a `SKILL.md` (and optional helper scripts).

| Skill | Script(s) | Purpose |
|-------|-----------|---------|
| `reconciliation` | `reconcile.py` | Match expenses against invoices, flag discrepancies |
| `slide-creator` | *(No script — prompt-based)* | Generate premium Google-style interactive HTML presentations |
| `vendor-verification` | `verify_vendors.py` | Look up expense merchants in Wikidata open CC0 database |

## Execution Order

Run strictly in order:

1. `reconciliation` → `reconciliation_report.md`, `reconciliation_data.json`
2. `slide-creator` → `reports/vendor_slideshow.html` (written directly by you based on the reconciliation data)
3. `vendor-verification` (Optional) → `vendor_verification_report.md`, `vendor_verification_data.json`

> [!NOTE]
> Step 2 (slideshow) and Step 3 (vendor verification) can optionally use `reconciliation_data.json` from step 1 as input. They can also run independently using `expenses.csv` directly.

## Analysis Rules

- **Scale**: Use Python to load and compare the data.
- **Generality**: Automatically match expenses to invoices based on common fields (date, merchant, amount, employee). Handle fuzzy matching if names differ slightly.
- **Discrepancy Detection**: Flag the following types of discrepancies:
  1. **Amount Mismatch**: The amount on the invoice does not match the expense record.
  2. **Missing Invoice**: An expense exists but no matching invoice is found.
  3. **Unmatched Invoice**: An invoice exists but no matching expense record is found.
  4. **Merchant Mismatch**: The merchant name on the invoice differs significantly from the expense record.
- **Report**: Produce a structured report (`reconciliation_report.md`) listing all flagged discrepancies with clear details.

## File Locations

| What | Path |
|------|------|
| Expense data | `./workspace/expenses.csv` |
| Invoice documents | `./workspace/` and `./workspace/invoices/` |
| Reconciliation report | `./workspace/reconciliation_report.md` |
| Reconciliation data | `./workspace/reconciliation_data.json` |
| HTML slideshow | `./workspace/reports/vendor_slideshow.html` |
| Verification report | `./workspace/vendor_verification_report.md` |
| Verification data | `./workspace/vendor_verification_data.json` |

## Edge Cases

- **Invoice extraction failures**: If Gemini cannot parse an invoice, the reconciliation script logs a warning and skips that file.
- **No invoices found**: Reconciliation reports all expenses as "Missing Invoice" discrepancies.
- **Empty expenses.csv**: Scripts exit gracefully with an informative message.
- **Rate limits**: Retry once with a brief pause for API calls.
- **Wikidata rate limits**: The script uses an explicit User-Agent. If rate-limited, it handles errors gracefully and reports merchants as Unverified.
