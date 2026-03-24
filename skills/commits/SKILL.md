---
name: commits
description: Formats commit messages.
---

## Rules
- The agent MUST analyze the staged changes and determine the commit type: `feat`, `fix`, `refactor`, or `chore`.
- The agent MUST inspect the current branch name before asking the user for an issue code.
- If the branch name contains an issue identifier, the agent MUST use it as the default and ask the user for confirmation.
- Supported issue identifiers are either a numeric ID such as `1234` or a tracker-style code such as `DSC-1111`.
- If no issue identifier is found in the branch name, the agent MUST ask the user: `What is the GitHub issue code for this work? (Enter the number, tracker code, or 'none')`.
- The description MUST use the imperative mood, for example `add loyalty endpoint` rather than `added loyalty endpoint`.
- The agent MUST NOT commit until the user has responded to the issue code prompt or confirmation question.

## Commit Message Format
- If the issue code is numeric, use: `<type>: [#1234] <description>`
- If the issue code is tracker-style, use: `<type>: [DSC-1111] <description>`
- If the user says `none`, use: `<type>: <description>`
- The agent SHOULD use `git commit -m "[generated message]"` after confirmation.
