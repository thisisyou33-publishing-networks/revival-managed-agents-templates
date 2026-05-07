#!/usr/bin/env python3
"""Generate background music for AI Radio using the Interactions API + Lyria.

Usage:
    python generate_music.py --workspace ./workspace
    python generate_music.py --workspace ./workspace --mood chill

Requires:
    pip install google-genai
    GEMINI_API_KEY environment variable

Output:
    {workspace}/audio/music/background.mp3
"""

import argparse
import base64
import os
from google import genai

MOOD_PROMPTS = {
    "news": (
        "Create a 30-second dramatic, urgent intro music track. "
        "Fast synth pulses, driving electronic beat, authoritative and serious tone. "
        "Perfect for a news or current affairs program. "
        "Instrumental only, no vocals. High energy and attention-grabbing."
    ),
    "chill": (
        "Create a 30-second subtle ambient track. "
        "Soft pads, gentle electric piano, light warm beats. "
        "Perfect as background music for a calm conversation. "
        "Instrumental only, no vocals. Relaxing and non-distracting."
    ),
    "tech": (
        "Create a 30-second modern electronic radio show intro track. "
        "Clean synths, subtle electronic pulse, forward-looking and innovative sound. "
        "Think cutting-edge technology and innovation. "
        "Instrumental only, no vocals."
    ),
    "debate": (
        "Create a 30-second dramatic discussion show intro track. "
        "Building tension, confident synth brass, measured intensity. "
        "Think panel discussion or current events show opener. "
        "Instrumental only, no vocals. Authoritative but not aggressive."
    ),
}

# Default mood
MOOD_PROMPTS["default"] = MOOD_PROMPTS["news"]

VALID_MOODS = list(MOOD_PROMPTS.keys())


def main():
    parser = argparse.ArgumentParser(description="Generate background music with Lyria")
    parser.add_argument("--workspace", default="workspace", help="Workspace directory")
    parser.add_argument(
        "--mood",
        default="default",
        choices=VALID_MOODS,
        help=f"Music mood: {', '.join(VALID_MOODS)}",
    )
    args = parser.parse_args()

    client = genai.Client()
    out_dir = os.path.join(args.workspace, "audio", "music")
    os.makedirs(out_dir, exist_ok=True)

    prompt = MOOD_PROMPTS[args.mood]

    print(f"=== AI Radio: Music Generation ===\n")
    print(f"Mood: {args.mood}")
    print("Generating background music via Interactions API (Lyria)...")

    def generate_music(prompt_text):
        try:
            interaction = client.interactions.create(
                model="lyria-3-clip-preview",
                input=prompt_text,
                store=False,
            )

            for output in interaction.outputs:
                if output.type == "audio":
                    out_path = os.path.join(out_dir, "background.mp3")
                    with open(out_path, "wb") as f:
                        f.write(base64.b64decode(output.data))
                    size_kb = os.path.getsize(out_path) / 1024
                    print(f"\n✅ Music saved to {out_path} ({size_kb:.0f} KB)")
                    return True
                elif output.type == "text":
                    print(f"   Lyria note: {output.text[:200]}")

            print("⚠️  No audio returned from Lyria.")
            return False

        except Exception as e:
            print(f"⚠️  Music generation failed: {e}")
            return False

    success = generate_music(prompt)

    if not success:
        print("\n🔄 Attempting retry with simpler fallback prompt...")
        fallback_prompt = "Create a 30-second simple ambient background track. Instrumental only, calm and neutral."
        success = generate_music(fallback_prompt)

    if not success:
        print("\n❌ Both attempts failed. Proceeding without background music.")


if __name__ == "__main__":
    main()
