---
name: pdf-parsing
description: Exposes a 100% local, offline PDF batch extraction utility (extract_to_markdown.py) that isolates invoices under invoices/ and translates PDFs into clean Markdown files for LLM-native parsing.
---

# PDF Invoice Local Extraction

This skill exposes a 100% offline, local PDF batch extraction utility (`extract_to_markdown.py`) that isolates all invoice documents inside the `invoices/` directory and exports them into clean, readable Markdown files (`.md`).

This runs entirely offline without any external network, server, or API key dependencies. This decouples raw text extraction from structuring, allowing you (the LLM agent) to perform robust, flexible data extraction natively without relying on fragile regular expressions.

## Batch Extraction Tool: `extract_to_markdown.py`

Processes a directory of PDF invoices sequentially, isolating all PDFs into a dedicated `invoices/` subdirectory and converting each to a matching `.md` file.

```bash
python3 skills/pdf-parsing/scripts/extract_to_markdown.py --workspace .agents/workspace
```

* **Standard PDF Files**: Uses `pypdf` locally to instantly extract text and save it as `<filename>.md` under `.agents/workspace/invoices/`.

---

## Agent Orchestration Guidelines

As the LLM agent, you should coordinate the invoice structuring workflow as follows:

1. **Move and Batch Extract**: Execute the batch extraction tool:
   ```bash
   python3 /.agents/skills/pdf-parsing/scripts/extract_to_markdown.py --workspace .agents/workspace
   ```
   This isolates all invoices inside `.agents/workspace/invoices/` and populates the folder with matching `<invoice_name>.md` files.

2. **LLM-Native Structuring**: Read the generated `.md` files under `.agents/workspace/invoices/`. Use your own agent reasoning (LLM context) to natively extract the structured fields from the markdown:
   - `merchant_name`
   - `date` (format: `YYYY-MM-DD`)
   - `amount` (float)
   - `invoice_number`
   - `source_file`

3. **Compile Structured Database**: Combine all structured invoice objects into a single JSON list and save it directly as `.agents/workspace/parsed_invoices.json` using your file creation tools, matching this schema:
   ```json
   [
     {
       "date": "2026-05-15",
       "merchant_name": "Google",
       "amount": 150.00,
       "invoice_number": "INV-GCP-1029",
       "source_file": "google_invoice.png"
     }
   ]
   ```

### Dependencies

- `pypdf` (>= 4.0.0)
