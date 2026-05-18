# AI Talk Radio Template

A template for [Managed Agents using the Gemini API](https://ai.google.dev/gemini-api/managed-agents). This agent turns a content source, such as Hacker News stories, GitHub repository changelogs, research papers, or a website URL, into a produced radio show by drafting scripts, synthesizing natural-sounding speech with telephonic audio effects, and mixing background ambient music.

---

## 🚀 Features

*   **Autonomous Research**: Integrates with Google Search and specialized web scraping scripts to gather grounded facts.
*   **Dynamic Script Writing**: Generates multiple character perspectives (hosts and callers) with adjustable show formats.
*   **High-End Audio Mixing**: Automates text-to-speech synthesis, Lyria background music generation, and audio blending with professional fades.
*   **Automatic Metadata**: Automatically outputs formatted show summaries, transcripts, and cover image designs.

---

## 🛠️ Code Snippet Placeholder

```bash
cd ai-radio
gemini-api agents test --prompt "Generate a 3-minute radio show called Daily Hacker Bites based on top Hacker News stories."
```

---

## 🧪 Testing the Prober

To quickly test the template end-to-end, run:

```bash
export GEMINI_API_KEY="your_api_key_here"
./probers.sh
```
