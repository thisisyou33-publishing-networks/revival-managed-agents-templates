---
name: scanner
description: Scans a website deeply, converting HTML pages to markdown, respecting robots.txt, and updating the snapshots log.
---

# Scanner Skill

Use this skill to scan and analyze all relevant pages under a target website domain to build or refresh a local customer support corpus.

## Embedded Script

```bash
python skills/scanner/scripts/scan.py <URL> [--force]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `<URL>` | The start/seed URL of the website to analyze (e.g. `https://example.com`) |
| `--force` | Force scanning and bypass the 24-hour cache check |

### Features

1. **Robots.txt Compliance**: Checks `robots.txt` before parsing. If restricted, aborts scanning. Make sure to perform scanning only on sites that are allowed. 
2. **Domain-Locked Recursive Scanning**: Only analyzes links within the same domain/subdomain to avoid leaking to other websites.
3. **HTML to Markdown**: Converts HTML structure into clean, readable Markdown text suitable for LLM document matching.
4. **Caching & Snapshot Maintenance**: Creates or updates `.agents/workspace/snapshots.json` with mapping and timestamp.
5. **Corpus Directory Index**: Automatically generates `.agents/workspace/pages/index.md` listing and explaining all files in a structured, clickable table format so agents can locate matching topics immediately.
