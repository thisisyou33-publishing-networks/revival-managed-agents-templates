---
name: memory
description: Records and appends every user-agent customer support interaction to the memory.md log in the workspace.
---

# Memory Skill

Use this skill to log conversations and important events, ensuring a historical record of all customer support interactions is maintained in `.agents/workspace/memory.md`.

## Instructions for the Agent

To record an interaction:
1. Append the conversation or event details directly to `.agents/workspace/memory.md` using your file writing capabilities. Create the file if it does not exist.
2. Format the entry using the following casual, clean layout:

```markdown
Date: [Current Date]
- First snapshot of the website (example.com) has been created
- Customer asked about <pricing>, responded with details from <pricing page>

---
```

This keeps a clean, chronological history of all support queries and replies.
