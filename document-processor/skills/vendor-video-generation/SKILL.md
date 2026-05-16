---
name: vendor-video-generation
description: Generate a video highlighting the highest-paid vendor from expense data, using Veo with animated GIF fallback.
---

# Vendor Video Generation

Generate a short video highlighting the vendor with the highest total payout from expense data. Uses Veo for video generation, with an automatic fallback to animated GIF (via Gemini image generation + Pillow) if Veo is unavailable.

## Embedded Script

```bash
python3 skills/vendor-video-generation/scripts/generate_vendor_video.py --workspace ./workspace
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--workspace` | `workspace` | Workspace directory containing expenses.csv |

### What it does

1. Loads expense data from `{workspace}/expenses.csv` (or `{workspace}/reconciliation_data.json` if available from a prior reconciliation run).
2. Aggregates total payouts by vendor/merchant.
3. Identifies the highest-paid vendor with total amount and percentage of total spend.
4. Uses Gemini `interactions.create()` with `gemini-3-flash-preview` to generate a narrative summary about the vendor.
5. Attempts video generation via **Veo** (`veo-2.0-generate-preview`) using `interactions.create()`.
6. On Veo failure, falls back to generating 4 image frames with `gemini-3.1-flash-image-preview` and assembling them into an animated GIF using Pillow.
7. Saves video/GIF and a summary JSON file.

### Dependencies

- `google-genai` (>= 2.0.0)
- `Pillow` (>= 10.0.0) — for GIF fallback assembly

## Output

| File | Path | Description |
|------|------|-------------|
| Video (primary) | `{workspace}/videos/top_vendor.mp4` | Veo-generated video clip |
| GIF (fallback) | `{workspace}/videos/top_vendor.gif` | Animated GIF from Gemini image frames |
| Summary JSON | `{workspace}/data/top_vendor_summary.json` | Vendor name, amount, percentage, narrative, video path |

## Fallback

Veo (`veo-2.0-generate-preview`) is experimental. If video generation fails, the script automatically:

1. Generates 4 image frames using `gemini-3.1-flash-image-preview` with business infographic-style prompts.
2. Assembles the frames into an animated GIF (2 seconds per frame) using Pillow.
3. Saves the GIF as `{workspace}/videos/top_vendor.gif`.

If both Veo and the GIF fallback fail, the script completes with just the summary JSON — no video output.
