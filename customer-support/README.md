# Customer Support Template

A template for building [Managed Agents using the Gemini API](https://ai.google.dev/gemini-api/managed-agents). This agent scans and indexes company documentation, API references, or website pages to answer customer support queries with grounded, factual accuracy.

---

## 🚀 Features

*   **Secure Web Scanner**: Indexes allowlisted websites to convert online documentation into a structured local Markdown corpus.
*   **Grounded Factual QA**: Answers user questions solely based on crawled snapshots.
*   **Persistent Interaction Memory**: Appends chronological conversation summaries to the persistent workspace memory file.
*   **Conversational Momentum**: Reads indexes and suggests 3-4 highly tailored specific topics of interest proactively.

---

## 🛠️ Code Snippet Placeholder

```bash
cd customer-support
gemini-api agents test --prompt "Build Gemini API customer support bot grounded with ai.google.dev/gemini-api/docs."
```

---

## 🧪 Testing the Prober

To quickly test the template end-to-end, run:

```bash
export GEMINI_API_KEY="your_api_key_here"
./probers.sh
```
