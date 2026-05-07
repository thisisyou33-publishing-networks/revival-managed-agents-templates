---
name: cover-image-generation
description: Generate cover images for the radio show using Gemini 3 Pro Image (Nano Banana Pro).
---

# Image Generation Skill

This skill generates an appropriate cover image for the radio show based on a prompt, using the Gemini 3 Pro Image model ("Nano Banana Pro").

## Requirements

- Python 3.10+
- `google-genai` Python package
- `GEMINI_API_KEY` environment variable

## Instructions

1. **Generate an image**:
   ```bash
   python skills/cover-image-generation/scripts/generate_image.py \
     --workspace ./workspace \
     --prompt "A prompt describing the image"
   ```

2. **Output**:
   - The image will be saved to `{workspace}/images/cover.png`.

## Model

- Model: `gemini-3-pro-image-preview`
- Resolution: 16:9 (default)

## Prompting rules

This skill uses a set of predefined prompt templates and selects one at random to generate cover images. It dynamically inserts the show title into the selected template.

- **Example Prompt**: `"A professional podcast cover image for a show titled 'AI Radio' on the 'AI Radio' station. The design features the text 'AI Radio' in a bold, stylish white font centered on the cover. The background is a vibrant purple with a textured water ripple effect that covers the entire frame, creating a dynamic and clean aesthetic."`

## Forbidden themes

- Do not ask for futuristic, cyberpunk or neon themes
- Do not include any text other than the show title

