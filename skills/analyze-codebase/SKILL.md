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
1. Decide whether the repository reconnaissance is trivial or non-trivial. Keep trivial, already-localized work in the parent session.
2. For non-trivial reconnaissance, preferably dispatch a fresh named `codebase-reader` when that profile is supported. The parent remains responsible for interpreting the result and verifying it against the repository.
3. Give the reader a concrete, task-directed request containing:
   - the concrete user task and the question the reconnaissance must answer
   - the repository root and any known scope (paths, modules, or symbols)
   - the user's constraints and relevant implementation boundaries
   - a request for only enough context to answer the task, not an exhaustive repository survey
4. If the `codebase-reader` profile cannot be resolved or delegation is unavailable, perform the same analysis in the parent session rather than failing.
5. Identify the entry points, modules, and files likely involved.
6. Trace the main call flow and dependency direction.
7. Find interfaces, implementations, models, and integration boundaries.
8. Note the patterns already used in this area.
9. Highlight ambiguities, missing context, and likely change points.

# Rules
- Prefer existing repository patterns over inferred ideal structures.
- Focus on only the code relevant to the task.
- Distinguish facts from hypotheses.
- Do not recommend refactors unless they are directly relevant.
- Delegation is optional and task-directed; never make model selection part of this skill or hard-code a model.
- Limit reconnaissance to the relevant scope and stop once there is enough evidence to answer the task.

# Optional reader delegation
When delegation is used, ask the fresh `codebase-reader` for a concise handback with exactly the context needed for the parent to proceed. It should cover:

- relevant files and modules
- current flow summary
- boundaries and dependencies involved
- existing patterns to follow
- likely change points
- questions, contradictions, and risks
- facts versus hypotheses, clearly separated

The reader reports evidence and uncertainty; it does not interpret the task for the parent, choose a model, edit files, or replace verification. The parent must check important claims against the repository and retain responsibility for the final analysis.

# Output
Provide:
- relevant files and modules
- current flow summary
- boundaries and dependencies involved
- existing patterns to follow
- open questions or risks before implementation
- likely change points
- facts distinguished from hypotheses
