---
name: github-researcher
description: Guides the agent on how to read and search GitHub issues to understand the repository's problems.
---

# GitHub Researcher Skill

This skill helps the agent find and understand issues in a specified GitHub repository, and gain a deep understanding of the codebase.

## Workflow

### 1. Fetching Issues

You can fetch issues using the provided Python script (works without auth for public repos):

```bash
python skills/github-researcher/scripts/fetch_issues.py --repo <owner>/<repo> --workspace ./workspace
```

Output: `{workspace}/data/github-issues.md`

Alternatively, if the environment is authenticated, you can use the GitHub CLI (`gh`):

```bash
gh issue list --repo <owner>/<repo> --state open --limit 20
```

### 2. Reading Issue Details
To understand a specific problem deeply:
```bash
gh issue view <issue_number> --repo <owner>/<repo> --comments
```

### 3. Understanding the Repo
To answer questions like *"What are my biggest issues?"* or understand the project deeply:
1. **Read the README**: Check the top-level `README.md` in the cloned repo.
2. **Scan the directory tree**: Use `find . -maxdepth 2` to understand the structure.
3. **Summarize issues**: Read the fetched issues and identify themes, recurring complaints, or critical bugs.

## Output

Produce a summary of the top issues and codebase structure to answer the user's high-level questions.
