# Agent Instructions: Reconciliation Agent

## What This Agent Does
This agent performs a reconciliation between expense transactions and invoices in the workspace. It reads a list of expenses from a CSV file and compares them with corresponding invoice documents (PDFs or Images). It flags any discrepancies, such as amount mismatches, merchant mismatches, or missing documents.

## Workspace Paths
The agent operates in the `./workspace/` directory. It expects to find `expenses.csv` and a set of invoice files (PDF or Image) there.

## Rules
- **Scale**: Use Python to load and compare the data.
- **Generality**: The agent must dynamically match expenses to invoices based on common fields (e.g., date, merchant, amount, employee) and handle fuzzy matching if names differ slightly.
- **Discrepancy Detection**: Flag the following types of discrepancies:
  1. **Amount Mismatch**: The amount on the invoice does not match the expense record.
  2. **Missing Invoice**: An expense exists but no matching invoice is found.
  3. **Unmatched Invoice**: An invoice exists but no matching expense record is found.
  4. **Merchant Mismatch**: The merchant name on the invoice differs significantly from the expense record.
- **Report**: Produce a structured report (`./workspace/reconciliation_report.md`) listing all flagged discrepancies with recommendations.

## Quick Start

```bash
# Run the agent
gemini-api agents test --prompt "Reconcile all expenses and generate vendor reports"
```

> [!TIP]
> After the agent completes, it prints an `environment_id`. Use that ID with `gemini-api files download <environment_id>` to pull all generated files to your local machine.

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
> - Chain sequential bash commands using `&&` in a single tool call (e.g., `python3 reconcile.py && python3 generate_slideshow.py`).

Upon execution, you should:

1. **Reconcile** — use `reconciliation` skill to match expenses in `expenses.csv` against invoice documents in the workspace. Extracts data from PDFs/images using Gemini, performs fuzzy matching, and flags discrepancies.
2. **Generate Video** — use `vendor-video-generation` skill to create a video (or animated GIF) highlighting the highest-paid vendor based on expense data.
3. **Generate Slideshow** — use `vendor-slideshow` skill to build a self-contained HTML slideshow presenting the top 3 highest-cost vendors with charts, AI-generated insights, and auto-advance navigation.

> [!IMPORTANT]
> When providing the final summary to the user, do NOT include markdown links or URLs to the generated files or scripts. Just use the plain file name (e.g., `reconcile.py`). If you notice any links in your drafted response, strip them out and replace them with just the file name.

## Architecture

```
User prompt
  ├── 1. python3 /.agents/skills/reconciliation/scripts/reconcile.py --workspace ./workspace
  │       → {workspace}/reconciliation_report.md
  │       → {workspace}/reconciliation_data.json
  ├── 2. python3 /.agents/skills/vendor-video-generation/scripts/generate_vendor_video.py --workspace ./workspace
  │       → {workspace}/videos/top_vendor.mp4 (or .gif)
  │       → {workspace}/data/top_vendor_summary.json
  └── 3. python3 /.agents/skills/vendor-slideshow/scripts/generate_slideshow.py --workspace ./workspace
          → {workspace}/reports/vendor_slideshow.html
```

## API Surface

All Gemini API calls use the **Interactions API** (`client.interactions.create()`), NOT `generateContent`:

| Step | Model | API |
|------|-------|-----|
| Invoice data extraction | `gemini-3-flash-preview` | `interactions.create()` |
| Narrative generation | `gemini-3-flash-preview` | `interactions.create()` |
| Video generation | `veo-2.0-generate-preview` | `interactions.create()` |
| Image generation (GIF fallback) | `gemini-3.1-flash-image-preview` | `interactions.create()` |

## Skills

Each skill lives in `/.agents/skills/<name>/` with a `SKILL.md` and a `scripts/` directory containing ready-to-run Python scripts.

| Skill | Script(s) | Purpose |
|-------|-----------|---------|
| `reconciliation` | `reconcile.py` | Match expenses against invoices, flag discrepancies |
| `vendor-video-generation` | `generate_vendor_video.py` | Video/GIF of the highest-paid vendor |
| `vendor-slideshow` | `generate_slideshow.py` | HTML slideshow of top 3 vendors |

## Execution Order

Skills can be run independently or in sequence. For a full analysis pipeline, run in order:

1. `reconciliation` → `reconciliation_report.md`, `reconciliation_data.json`
2. `vendor-video-generation` → `videos/top_vendor.mp4` (or `.gif`), `data/top_vendor_summary.json`
3. `vendor-slideshow` → `reports/vendor_slideshow.html`

> [!NOTE]
> Step 2 (video generation) can optionally use `reconciliation_data.json` from step 1 as input. Steps 2 and 3 can also run independently using `expenses.csv` directly.

## Data Format

### expenses.csv

| Column | Type | Description |
|--------|------|-------------|
| `date` | string | Expense date |
| `employee` | string | Employee who submitted the expense |
| `merchant` | string | Vendor/merchant name |
| `category` | string | Expense category |
| `amount` | float | Expense amount in dollars |
| `memo` | string | Notes or description |

### Invoice Files

The workspace may contain invoice documents as PDF or image files (`.pdf`, `.png`, `.jpg`, `.jpeg`). These are located in the workspace root or in an `invoices/` subdirectory.

## File Locations

| What | Path |
|------|------|
| Expense data | `./workspace/expenses.csv` |
| Invoice documents | `./workspace/` and `./workspace/invoices/` |
| Reconciliation report | `./workspace/reconciliation_report.md` |
| Reconciliation data | `./workspace/reconciliation_data.json` |
| Vendor video/GIF | `./workspace/videos/top_vendor.mp4` (or `.gif`) |
| Vendor summary | `./workspace/data/top_vendor_summary.json` |
| HTML slideshow | `./workspace/reports/vendor_slideshow.html` |

## Edge Cases

- **Invoice extraction failures**: If Gemini can't parse an invoice, the reconciliation script logs a warning and skips that file.
- **Veo availability**: Experimental model. If video generation fails, the script falls back to generating an animated GIF from Gemini-generated image frames.
- **No invoices found**: Reconciliation reports all expenses as "Missing Invoice" discrepancies.
- **Empty expenses.csv**: Scripts exit gracefully with an informative message.
- **Rate limits**: Retry once with a brief pause for API calls.

## Downloading Results

After a test run, the CLI outputs an `environment_id`. Use it to download the generated files:

```bash
# Download the workspace snapshot
gemini-api files download <environment_id>
```

This will download and extract a directory `snapshot_<environment_id>/` containing the workspace files (such as the reports, videos, and summaries).
