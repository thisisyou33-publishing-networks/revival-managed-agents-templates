# Repo Maintainer Template

A template for building [Managed Agents using the Gemini API](https://ai.google.dev/gemini-api/managed-agents). This agent analyzes GitHub repositories. It clones git repositories, analyzes open GitHub issues, implements bug fixes, and exports standardized `.patch` files for review.

---

## 🚀 Features

*   **Repository Analysis**: Clones and maps out project directory structures to trace codebase flows.
*   **Issue Auditing**: Retrieves and analyzes open bugs.
*   **Safe Code Fixes**: Creates dedicated local Git branches to test and apply code changes locally.
*   **Standardized Patches**: Generates standard, ready-to-apply `.patch` files using `git format-patch` or `git diff`.

---

## 🛠️ Code Snippet Placeholder

```bash
cd repo-maintainer
gemini-api agents test --prompt "Clone https://github.com/googleapis/python-genai and give me an overview of the repository structure and README."
```

---

## 🧪 Testing the Prober

To quickly test the template end-to-end, run:

```bash
export GEMINI_API_KEY="your_api_key_here"
./probers.sh
```
