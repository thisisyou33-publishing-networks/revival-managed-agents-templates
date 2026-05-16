---
name: vendor-slideshow
description: Generate a self-contained HTML slideshow presenting the top 3 highest-cost vendors with charts, AI-generated insights, and auto-advance.
---

# Vendor Slideshow

Generate a premium, self-contained HTML slideshow presenting the top highest-cost vendors from expense data. Features AI-generated executive insights, inline SVG charts, glassmorphism design, and smooth auto-advancing navigation.

## Embedded Script

```bash
python3 skills/vendor-slideshow/scripts/generate_slideshow.py --workspace ./workspace
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--workspace` | `workspace` | Workspace directory containing expenses.csv |
| `--top` | `3` | Number of top vendors to feature in the slideshow |

### What it does

1. Loads expense data from `{workspace}/expenses.csv` (columns: date, employee, merchant, category, amount, memo).
2. Aggregates total costs by merchant, ranks them, and identifies the top N vendors.
3. For each top vendor, computes: total spend, percentage of grand total, category breakdown, transaction count.
4. Uses Gemini `interactions.create()` with `gemini-3-flash-preview` to generate executive-level narrative insights for each vendor.
5. Builds a self-contained HTML file with embedded CSS and JavaScript — no external dependencies (except Google Fonts via `@import`).
6. Saves to `{workspace}/reports/vendor_slideshow.html`.

### Dependencies

- `google-genai` (>= 2.0.0)

## Slides

| Slide | Content |
|-------|---------|
| **Title** | "Vendor Cost Analysis" header, report date, total spend, vendor count |
| **Vendor Detail** (×N) | Rank badge, vendor name, total spend, % of total, category breakdown bars (inline SVG), AI insight, transaction count |
| **Summary** | Comparison bar chart (inline SVG) with all featured vendors side by side, total analyzed spend |

## Design

- **Background**: Dark theme (`#0f0f1a`)
- **Accents**: Purple-to-blue gradient (`#7c3aed` → `#2563eb`)
- **Cards**: Glassmorphism — semi-transparent background, `backdrop-filter: blur(20px)`, subtle border
- **Typography**: Google Font 'Inter' via `@import`
- **Transitions**: Smooth slide transforms with CSS `transform` + `opacity`, 0.6s ease
- **Charts**: Inline SVG — no external charting libraries

## Navigation

- **Auto-advance**: Every 8 seconds
- **Manual**: Left/right arrow keys, click to advance
- **Indicators**: Dot indicators at bottom of the viewport
- **Pause**: Auto-advance pauses on hover, resumes on mouse leave

## Output

| File | Path | Format |
|------|------|--------|
| HTML Slideshow | `{workspace}/reports/vendor_slideshow.html` | Self-contained HTML |
