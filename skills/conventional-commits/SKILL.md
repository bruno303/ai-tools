---
name: conventional-commits
description: Formats commit messages.
---

## Instructions for Agent
1. **Analyze Changes**: Look at the staged changes to determine the commit type (`feat`, `fix`, `refactor`, or `chore`).
2. **User Interaction**: Before committing, ask the user: "What is the github issue code for this work? (Enter the number or 'none')".
3. **Format Logic**:
   - If user provides a code (e.g., "1234"), the format is: `<type>: [#1234] <description>`
   - If user says "none", the format is: `<type>: <description>`
4. **Description**: Ensure the description is in the imperative mood (e.g., "add loyalty endpoint" not "added loyalty endpoint").

## Constraint
- Do NOT commit until the user has responded to the task code prompt.
- Use `git commit -m "[generated message]"` after confirmation.
