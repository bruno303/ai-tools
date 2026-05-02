---
name: analyze-codebase
description: Use when starting work in an unfamiliar code area to identify relevant files, call flow, boundaries, dependencies, and patterns to follow.
---

# When to use
Use for:
- new features in an unfamiliar module
- bug fixing when the cause is not yet localized
- tasks that require understanding how a behavior is wired today

Do not use for:
- trivial changes in code that is already well understood
- final review after implementation

# Goal
Build a concise map of the relevant area before planning or editing code.

# Process
1. Identify the entry points, modules, and files likely involved.
2. Trace the main call flow and dependency direction.
3. Find interfaces, implementations, models, and integration boundaries.
4. Note the patterns already used in this area.
5. Highlight ambiguities, missing context, and likely change points.

# Rules
- Prefer existing repository patterns over inferred ideal structures.
- Focus on only the code relevant to the task.
- Distinguish facts from hypotheses.
- Do not recommend refactors unless they are directly relevant.

# Output
Provide:
- relevant files and modules
- current flow summary
- boundaries and dependencies involved
- existing patterns to follow
- open questions or risks before implementation
