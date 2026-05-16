---
name: pdf-parsing
description: Exposes two atomic data extraction tools (extract_pypdf and extract_gemini) to parse PDF/image invoices, putting orchestration and fallback decisions directly in the agent's hands.
---

# PDF Invoice Parsing

This skill exposes two focused, atomic extraction tools to the agent, allowing the agent's own planning brain to coordinate the workflow, handle fallbacks, and write the structured results database.

## Atomic Tools Exposed

### 1. Local Text Extractor (`extract_pypdf.py`)
Extracts raw text content from a PDF document locally.

```bash
python3 skills/pdf-parsing/scripts/extract_pypdf.py --file ./workspace/invoices/invoice.pdf
```
- **Returns**: Raw text printed to stdout.
- **Exit Code**: `0` on success, `1` on failure or empty text.

### 2. Visual Gemini Parser (`extract_gemini.py`)
Uploads a PDF or image file to Gemini and visually parses it into structured JSON.

```bash
python3 skills/pdf-parsing/scripts/extract_gemini.py --file ./workspace/invoices/invoice.png
```
- **Returns**: Structured JSON object matching the schema printed to stdout.
- **Exit Code**: `0` on success, `1` on failure.

---

## Agent Orchestration Guidelines

As the agent, you must coordinate these two tools for every invoice file:

1.  **Always try `extract_pypdf.py` first** for all PDF files.
    - **If successful**: Use your own language reasoning (LLM) to extract the required fields (`merchant_name`, `date`, `amount`, `invoice_number`) from the resulting raw text.
2.  **Use `extract_gemini.py` as a fallback** if `extract_pypdf.py` fails (returns no text), or if the file is an image (`.png`, `.jpg`, `.jpeg`).
3.  Compile all structured invoice objects into a single JSON list and save it as `{workspace}/parsed_invoices.json` matching this schema:
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

- `google-genai` (>= 2.0.0)
- `pypdf` (>= 4.0.0)
