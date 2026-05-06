#!/usr/bin/env python3
"""Generate TTS audio with telephone effect on correspondent voices using the Interactions API.

Usage:
    python generate_tts.py --workspace ./workspace

Requires:
    pip install google-genai
    ffmpeg (system)
    GEMINI_API_KEY environment variable

Output:
    {workspace}/audio/speech/speech.wav
"""

import argparse
import base64
import os
import subprocess
import time
import wave
from google import genai

# Voice mapping — each speaker gets a unique Gemini TTS voice
VOICE_MAP = {
    "Jordan": "Puck",     # Host — studio quality
}

FEMALE_VOICES = ["Kore", "Aoede"]
MALE_VOICES = ["Charon", "Fenrir"]

PROFILES = {
    "Jordan": {
        "profile": "# AUDIO PROFILE: Jordan\n## Role: Community Radio Host / Moderator\n## Persona: Calm, measured, intellectual, and polite British moderator.",
        "scene": "## THE SCENE: The London Studio\nA quiet, professional studio in London. Jordan is sitting calmly, speaking into a high-quality microphone.",
        "notes": "### DIRECTOR'S NOTES\nStyle: Calm, measured, polite, professional.\nPacing: Deliberate, steady.\nAccent: British English accent as heard in Croydon, England.",
    },
    "default_caller": {
        "profile": "# AUDIO PROFILE: Caller\n## Role: Tech-savvy individual calling in to a radio show.\n## Persona: Nerdy, conversational, not a professional broadcaster.",
        "scene": "## THE SCENE: Remote Location via Phone\nCalling in from a home, office, or public space. The audio quality is that of a telephone call.",
        "notes": "### DIRECTOR'S NOTES\nStyle: Conversational, natural.\nPacing: Normal conversational pace.\nAccent: American English.",
    },
}


def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    """Save raw PCM data as a WAV file."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)


def split_script_by_turns(script_text):
    """Parse script into ordered (speaker, text) turns."""
    turns = []
    for line in script_text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            speaker = line.split(':')[0].strip()
            text = ':'.join(line.split(':')[1:]).strip()
            if text:
                turns.append((speaker, text))
    return turns


def generate_tts_single(client, speaker, text, output_path, voice, accent):
    """Generate TTS for a single speaker turn using the Interactions API."""
    profile_data = PROFILES.get(speaker, PROFILES.get("default_caller", {}))
    
    notes = profile_data.get('notes', '')
    import re
    notes = re.sub(r'Accent:.*', f'Accent: {accent}', notes)
    
    prompt = f"""{profile_data.get('profile', '')}

{profile_data.get('scene', '')}

{notes}

#### TRANSCRIPT
{text}
"""

    interaction = client.interactions.create(
        model="gemini-3.1-flash-tts-preview",
        input=prompt,
        response_modalities=["audio"],
        generation_config={
            "speech_config": [{
                "voice": voice,
                "language": "en-US",
            }
            ]
        },
        store=False,
    )

    for output in interaction.outputs:
        if output.type == "audio":
            pcm_data = base64.b64decode(output.data)
            wave_file(output_path, pcm_data)
            return True

    return False


def apply_telephone_filter(input_path, output_path):
    """Apply telephone bandpass filter (300Hz-3400Hz) via ffmpeg.

    Simulates a phone call:
    1. Highpass at 300Hz — cuts rumble
    2. Lowpass at 3400Hz — cuts highs (telephone bandwidth)
    3. Compression — mimics phone codec dynamics
    4. Slight volume reduction
    """
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-af", (
            "highpass=f=300,"
            "lowpass=f=3400,"
            "acompressor=threshold=-20dB:ratio=4:attack=5:release=50,"
            "volume=0.95"
        ),
        output_path
    ], check=True, capture_output=True)


def concatenate_wav_files(file_list, output_path):
    """Concatenate WAV files (same format) into one."""
    all_pcm = b""
    for f in file_list:
        with wave.open(f, "rb") as wf:
            all_pcm += wf.readframes(wf.getnframes())
    wave_file(output_path, all_pcm)


def main():
    parser = argparse.ArgumentParser(description="Generate TTS with telephone effect")
    parser.add_argument("--workspace", default="workspace", help="Workspace directory")
    args = parser.parse_args()

    client = genai.Client()

    # Read script
    script_path = os.path.join(args.workspace, "data", "script.md")
    with open(script_path) as f:
        script = f.read()

    turns = split_script_by_turns(script)
    print(f"=== AI Radio: TTS Generation ===\n")
    print(f"Found {len(turns)} speaker turns\n")

    segments_dir = os.path.join(args.workspace, "audio", "speech", "segments")
    os.makedirs(segments_dir, exist_ok=True)

    segment_files = []
    assigned_voices = {"Jordan": "Puck"}
    assigned_accents = {"Jordan": "British English accent as heard in Croydon, England"}
    female_index = 0
    male_index = 0

    import re

    for i, (speaker, text) in enumerate(turns):
        raw_path = os.path.join(segments_dir, f"turn_{i:03d}_raw.wav")
        final_path = os.path.join(segments_dir, f"turn_{i:03d}.wav")

        # Parse gender tag
        gender = "Male"  # default
        if "[Female]" in text:
            gender = "Female"
            text = text.replace("[Female]", "").strip()
        elif "[Male]" in text:
            gender = "Male"
            text = text.replace("[Male]", "").strip()

        # Parse accent tag
        accent = "American English"  # default
        accent_match = re.search(r'\[Accent: ([^\]]+)\]', text)
        if accent_match:
            accent = accent_match.group(1)
            text = re.sub(r'\[Accent: [^\]]+\]', '', text).strip()

        if speaker not in assigned_voices:
            if gender == "Female":
                assigned_voices[speaker] = FEMALE_VOICES[female_index % len(FEMALE_VOICES)]
                female_index += 1
            else:
                assigned_voices[speaker] = MALE_VOICES[male_index % len(MALE_VOICES)]
                male_index += 1
            
        if speaker not in assigned_accents:
            assigned_accents[speaker] = accent
            
        voice = assigned_voices[speaker]
        accent = assigned_accents[speaker]

        print(f"  [{i+1}/{len(turns)}] {speaker} ({voice}, {accent}): {text[:60]}...")

        # Generate TTS via Interactions API
        try:
            success = generate_tts_single(client, speaker, text, raw_path, voice, accent)
            if not success:
                print(f"    ⚠ No audio returned, skipping")
                continue
        except Exception as e:
            print(f"    ERROR: {e}")
            time.sleep(5)
            try:
                success = generate_tts_single(client, speaker, text, raw_path, voice, accent)
                if not success:
                    continue
            except Exception as e2:
                print(f"    RETRY FAILED: {e2}, skipping")
                continue

        # Apply telephone filter for callers (not Jordan)
        if speaker != "Jordan":
            try:
                apply_telephone_filter(raw_path, final_path)
                print(f"    ✓ + telephone filter")
            except Exception:
                os.rename(raw_path, final_path)
                print(f"    ✓ (filter failed, using raw)")
        else:
            os.rename(raw_path, final_path)
            print(f"    ✓ clean studio")

        segment_files.append(final_path)
        time.sleep(1)  # Rate limit

    # Concatenate
    output_path = os.path.join(args.workspace, "audio", "speech", "speech.wav")
    concatenate_wav_files(segment_files, output_path)

    # Stats
    with wave.open(output_path, "rb") as wf:
        duration = wf.getnframes() / wf.getframerate()

    print(f"\n✅ TTS complete!")
    print(f"   Output: {output_path}")
    print(f"   Duration: {duration:.1f}s | Segments: {len(segment_files)}")


if __name__ == "__main__":
    main()
