---
name: project-coding-guidelines
description: Use for any development task that changes code. Applies repository-first rules for architecture, code placement, dependency direction, abstractions, and structural consistency. Load before implementing, refactoring, reviewing, or testing code so changes follow the project’s existing design instead of introducing new patterns.
---

# Architectural Guidelines

Apply these principles across all tasks unless the repository explicitly defines a different rule.

# General approach
- First identify the architecture already in use in the repository.
- Prefer extending existing patterns over introducing parallel ones.
- Choose the smallest change that fits the current structure.
- Keep responsibilities clear and local.
- Do not restructure large areas unless the task clearly requires it.

# Code placement
- Place new code near the existing code with the same responsibility.
- Keep business rules in the business/application layers, not in transport, framework, or persistence code.
- Keep infrastructure concerns out of domain logic unless the repository intentionally allows that coupling.
- Put shared code in shared locations only when it is truly reused by multiple parts of the system.

# Dependency direction
- Preserve the dependency direction already established by the project.
- Do not introduce dependencies from core/business layers into framework, transport, UI, or infrastructure layers unless the repository explicitly uses that pattern.
- Before adding an interface or abstraction, verify that it protects a real boundary rather than adding indirection without benefit.

# Abstractions and patterns
- Reuse existing seams, interfaces, and extension points before creating new ones.
- Add abstractions only when they simplify a real responsibility boundary, improve substitution, or reduce meaningful duplication.
- Avoid creating new patterns when an existing project pattern already solves the problem.
- Prefer explicit, easy-to-follow code over generalized structures introduced too early.

# Reviewing structural changes
When implementing or reviewing a change, check:
- whether the code is in the correct layer or module
- whether responsibilities are mixed
- whether dependency direction remains consistent
- whether the naming matches the actual responsibility
- whether a future reader would know where to extend the behavior

# Default behavior
- Preserve architectural consistency over personal preference.
- Prefer local adaptation to broad refactors.
- If the current architecture is imperfect, do not silently redesign it as part of an unrelated task.
- When architectural tradeoffs are necessary, explain them clearly.
