---
name: pdf-parsing
description: Extract structured data (merchant, date, amount, invoice number) from PDF and image invoices in the workspace, utilizing local pypdf text extraction with visual Gemini fallback.
---

# PDF Invoice Parsing

Extract structured data from invoice documents (PDFs and images) in the workspace. It utilizes local `pypdf` text extraction for high-speed, cost-effective processing of text-based PDFs, and automatically falls back to visual Gemini parsing for scanned PDFs and image files.

## Embedded Script

```bash
python3 skills/pdf-parsing/scripts/parse_invoices.py --workspace ./workspace
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--workspace` | `workspace` | Workspace directory containing invoice files |

### What it does

1. Scans the workspace and `invoices/` subdirectory for invoice files (`.pdf`, `.png`, `.jpg`, `.jpeg`).
2. For each invoice:
   - **Text-based PDF**: Attempts local text extraction with `pypdf`. If text is found, calls Gemini (`gemini-3-flash-preview`) with a fast, text-only prompt to parse the fields into structured JSON. No file upload is required!
   - **Scanned PDF or Image**: Falls back to the visual parsing method: uploads the file to the **Gemini Files API**, then calls Gemini (`gemini-3-flash-preview`) with a visual prompt.
3. Compiles all extracted invoices into a structured JSON list.
4. Saves results to `{workspace}/parsed_invoices.json`.

### Dependencies

- `google-genai` (>= 2.0.0)
- `pypdf` (>= 4.0.0)

## API Surface

All Gemini API calls in this script use the **Interactions API** (`client.interactions.create()`), NOT `generateContent`:

| Step | Model | API |
|------|-------|-----|
| Invoice data extraction | `gemini-3-flash-preview` | `interactions.create()` |

## Output

| File | Path | Format | Description |
|------|------|--------|-------------|
| Parsed Invoices | `{workspace}/parsed_invoices.json` | JSON List | Structured list of objects containing: `date`, `merchant_name`, `amount`, `invoice_number`, `source_file`. |
