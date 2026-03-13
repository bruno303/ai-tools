---
name: pr-ready
description: Orchestrates linting, smart test discovery, and PR documentation.
---

## Instructions for Agent

### Step 1: Linting & Formatting
- **Go Projects**: 
    - MUST find a `Makefile`. Run `make fmt` and `make lint`. 
    - If goals are missing, inform the user: "Go project detected but 'make lint/fmt' goals not found."

### Step 2: Smart Test Discovery
1. **Search Makefile First**: Look for goals named `test`, `tests`, `unit-test`, or `check`.
2. **User Confirmation**: If a matching goal is found, ask: "I found a 'make [goal]' command. Should I use this for testing? (y/n)".
3. **Fallback Logic**:
   - If user says **'y'**: Execute the Makefile goal.
   - If user says **'n'** OR **no goal is found**: 
     - **Go**: Execute `go test ./...`
4. **Summary**: Capture and summarize any failures.

### Step 3: PR Description Generation
If all checks pass (or user overrides a non-critical failure), generate this Markdown:

- **Summary**: 2-sentence explanation of changes.
- **Type**: (Feat/Fix/Refactor/Chore)
- **Task**: [#XXXX] (Auto-filled from last commit if possible)
- **Quality Check**: 
  - [ ] Linting (Command used: `...`)
  - [ ] Tests (Command used: `...`)

## Constraint
- Always report the specific command used for testing in the final summary so the user knows if it was the Makefile or the Fallback.
