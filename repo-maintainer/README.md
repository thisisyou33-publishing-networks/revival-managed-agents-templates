# Repo Maintainer Template

A template for building [Managed Agents using the Gemini API](TODO). This agent analyzes GitHub repositories. It clones git repositories, analyzes open GitHub issues, implements bug fixes, and exports standardized `.patch` files for review.

---

## 🚀 Features

*   **Repository Analysis**: Clones and maps out project directory structures to trace codebase flows.
*   **Issue Auditing**: Retrieves and analyzes open bugs.
*   **Safe Code Fixes**: Creates dedicated local Git branches to test and apply code changes locally.
*   **Standardized Patches**: Generates standard, ready-to-apply `.patch` files using `git format-patch` or `git diff`.

---

## 🛠️ Code Snippet Placeholder

```python
# TODO
```

---

## 🧪 Testing the Agent

To test the agent from the root of this repository:

```bash
cd repo-maintainer
gemini-api agents test --prompt "Hello, what are your instructions?"
```
