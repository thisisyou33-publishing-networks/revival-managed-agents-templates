#!/usr/bin/env python3
"""Generate cover image for AI Radio using Gemini 3 Pro Image (Nano Banana Pro).

Usage:
    python generate_image.py --workspace ./workspace --prompt "Futuristic radio station"

Requires:
    pip install google-genai
    GEMINI_API_KEY environment variable
"""

import argparse
import base64
import json
import os
import sys
import warnings
from google import genai

# Suppress experimental warnings from SDK
warnings.filterwarnings("ignore", message="Interactions usage is experimental")

def generate_image(prompt, output_path, reference=None, aspect_ratio="1:1"):
    client = genai.Client()

    print(f"Generating image with prompt: '{prompt}'")
    print("Using model: gemini-3-pro-image-preview")

    input_content = [{"type": "text", "text": prompt}]
    if reference and os.path.exists(reference):
        print(f"Uploading reference image {reference}...")
        ref_file = client.files.upload(file=reference)
        input_content.append({
            "type": "image",
            "uri": ref_file.uri
        })
        print(f"Uploaded as {ref_file.name}")

    try:
        interaction = client.interactions.create(
            model="gemini-3-pro-image-preview",
            input=input_content,
            response_modalities=["image"],
            generation_config={
                "image_config": {
                    "aspect_ratio": aspect_ratio
                }
            }
        )

        for output in interaction.outputs:
            if output.type == "image":
                image_data = base64.b64decode(output.data)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(image_data)
                print(f"✅ Image saved to {output_path}")
                return True

        print("⚠️  No image returned in response.")
        return False

    except Exception as e:
        print(f"⚠️  Image generation failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate cover image with Gemini")
    parser.add_argument("--workspace", default="workspace", help="Workspace directory")
    parser.add_argument("--prompt", help="Image prompt")
    parser.add_argument("--metadata", help="Path to show_notes.json metadata file")
    parser.add_argument("--output", help="Output image path")
    parser.add_argument("--reference", help="Reference image path for consistency")
    parser.add_argument("--aspect_ratio", default="1:1", help="Aspect ratio (e.g., 1:1, 16:9)")
    args = parser.parse_args()

    if not args.prompt and not args.metadata:
        parser.error("Either --prompt or --metadata must be provided")

    prompt = args.prompt

    if args.metadata:
        if not os.path.exists(args.metadata):
            print(f"ERROR: Metadata file not found at {args.metadata}")
            sys.exit(1)

        with open(args.metadata, "r") as f:
            metadata = json.load(f)

        title = metadata.get("show_title", "AI Radio")
        summary = metadata.get("two_sentence_summary", "")

        print(f"Generating prompt from metadata for title: '{title}'")

        prompt_gen_prompt = f"""You are a creative prompt engineer for an image generation model.
Generate a prompt for a podcast cover image based on the following show metadata:
Title: {title}
Summary: {summary}

Follow these rules strictly:
1. The prompt must describe a cover image that includes the title "{title}" as text with a stylish, bold font.
2. Do NOT include any humans, DJs, or hosts.
3. The background must be textured and interesting (e.g., halftone dots, abstract geometry, water ripples).
4. The design must feel integrated across the entire frame.
5. Do NOT use futuristic, cyberpunk, or neon themes.
6. Do NOT include any text other than the show title.

Return ONLY the prompt string.
"""

        client = genai.Client()
        interaction = client.interactions.create(
            model="gemini-3-flash-preview",
            input=prompt_gen_prompt,
        )

        if interaction.outputs:
             prompt = interaction.outputs[-1].text.strip()
             print(f"Generated prompt: '{prompt}'")
        else:
             print("ERROR: Failed to generate prompt from metadata.")
             sys.exit(1)

    output_path = args.output
    if not output_path:
        output_path = os.path.join(args.workspace, "images", "cover.png")

    success = generate_image(prompt, output_path, reference=args.reference, aspect_ratio=args.aspect_ratio)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
