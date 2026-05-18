# Customer Support Template

A template for building [Managed Agents using the Gemini API](TODO). This agent scans and indexes company documentation, API references, or website pages to answer customer support queries with grounded, factual accuracy.

---

## 🚀 Features

*   **Secure Web Scanner**: Indexes allowlisted websites to convert online documentation into a structured local Markdown corpus.
*   **Grounded Factual QA**: Answers user questions solely based on crawled snapshots.
*   **Persistent Interaction Memory**: Appends chronological conversation summaries to the persistent workspace memory file.
*   **Conversational Momentum**: Reads indexes and suggests 3-4 highly tailored specific topics of interest proactively.

---

## 🛠️ Code Snippet Placeholder

```python
# TODO
```

---

## 🧪 Testing the Agent

To test the agent from the root of this repository:

```bash
cd customer-support
gemini-api agents test --prompt "Hello, what are your instructions?"
```
