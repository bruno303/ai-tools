---
name: software-design
description: Use when a development task requires a structural design choice, such as adding or changing an abstraction, integration seam, persistence boundary, event flow, wrapper, or dependency wiring; refactoring repeated conditionals or lifecycle logic; or reviewing structural quality. Provides SOLID as diagnostic heuristics and a catalog of common patterns with explicit anti-over-abstraction guidance.
---

# Software Design

Use patterns and SOLID as named solutions to concrete problems, never as defaults
or a checklist to satisfy.

## When to use

Use for:

- adding or changing an abstraction, seam, or extension point
- introducing a persistence, integration, event, middleware, or dependency-wiring boundary
- refactoring repeated conditionals, duplicated construction, or lifecycle logic
- reviewing whether a structural change is justified
- naming patterns already present in an unfamiliar codebase

Do not use for:

- trivial edits, formatting, or renaming
- local bug fixes with no design choice
- work already covered by a clear repository convention
- replacing an established project pattern with a textbook alternative

## Process

1. State the concrete force or problem, including what becomes harder without a change.
2. Inspect existing repository patterns, language idioms, and similar code first.
3. Consider the simplest direct implementation and the option of changing nothing.
4. If a pattern is warranted, choose it with `references/pattern-selection.md` and
   name the rejected alternatives, including the direct implementation.
5. Apply SOLID as a diagnostic from `references/solid.md` to explain a specific
   smell, not to justify a rewrite.
6. Define how the new seam will be tested and how behavior remains verifiable.
7. Record the decision in the plan or change description when the choice is structural.

## Rules

- No pattern without a named problem it solves.
- Reuse existing repository patterns before adding a new one.
- Choose the smallest change that resolves the force.
- Prefer composition over inheritance.
- Add interfaces only at real boundaries, owned by the consumer.
- Prefer explicit constructor or parameter injection over global singletons or service locators.
- Do not add a repository, unit of work, event bus, or middleware "for consistency"
  unless the boundary or transaction actually requires it.
- Do not duplicate the same concept behind multiple abstractions.
- Treat "no pattern", "reuse the existing pattern", and "defer the abstraction" as
  first-class choices.

## References

- `references/solid.md` - SOLID heuristics, smells, safe refactors, and counterweights.
- `references/patterns.md` - catalog for the 14 common patterns.
- `references/pattern-selection.md` - problem-first selection table and similar-pattern discriminators.
- `references/review-checklist.md` - implementation and review questions.

Load only the reference file needed for the current decision.

## Output

When a design decision is material, provide a short design note:

- problem and forces
- chosen approach and why it fits the repository
- alternatives rejected, including the direct implementation
- tradeoffs and risks
- how the design will be tested
