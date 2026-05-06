---
name: music-generation
description: Generate ambient background music using Lyria via the Interactions API.
---

# Music Generation

Generate background music for the radio show using the Lyria model via the **Interactions API**.

## Embedded Script

```bash
python skills/music-generation/scripts/generate_music.py --workspace ./workspace --mood news
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--workspace` | `workspace` | Root workspace directory |
| `--mood` | `default` | Music mood (see moods below) |

### Moods

| Mood | Style | Pair with `--style` |
|------|-------|---------------------|
| `news` (default) | Urgent synth pulses, driving beat, BBC breaking news vibe | `debate` |
| `chill` | Soft pads, gentle piano, lo-fi warmth | `roundtable`, `explainer` |
| `tech` | Clean synths, electronic pulse, Silicon Valley startup vibe | `explainer` |
| `debate` | Building tension, brass-like synths, panel discussion opener | `debate`, `interview` |

### What it does

1. Selects the music prompt based on `--mood`.
2. Calls the **Interactions API** with the `lyria-3-clip-preview` model.
3. Generates a ~30-second music clip.
4. Saves as MP3 to `{workspace}/audio/music/background.mp3`.
5. Gracefully handles failures — the pipeline continues without music.

### Dependencies

- `google-genai` (>= 1.55.0)
- `GEMINI_API_KEY` environment variable

## Output

- **File**: `{workspace}/audio/music/background.mp3`
- **Format**: MP3
- **Duration**: ~30 seconds

## Fallback

Lyria is experimental. If generation fails, the pipeline proceeds without background music — the audio-mixing step handles this gracefully.
