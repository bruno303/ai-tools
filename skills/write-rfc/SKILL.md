---
name: write-rfc
description: Use when turning a PRD, issue, or set of requirements into an evidence-based RFC with clarified decisions, proportional sections, and explicit technical trade-offs before implementation planning.
---

# Write an RFC

## When to use

Use this skill when a feature needs a shared technical proposal before anyone
plans or implements it. It is appropriate for both a small, local change and a
large cross-system design. Do not use it as a substitute for implementation
planning or as a request to start coding.

## Workflow

1. Read the supplied PRD, issue, and supporting documents in full. Extract the
   problem, goals, non-goals, requirements, constraints, dependencies, and
   relevant context. Consult `references/examples.md` when useful for RFC scale,
   architectural decisions, or conflicting sources.
2. Before asking questions, inspect repository guidance (`AGENTS.md`,
   `CLAUDE.md`, and equivalent), analogous features, interfaces, tests, and
   configuration. Prefer repository evidence to guesses.
3. Label claims as **source fact**, **repository evidence**, **technical inference**,
   **proposed decision**, **assumption**, **contradiction**, or **unresolved question**.
   Keep those categories visibly distinct. Every material source fact and piece of
   repository evidence must cite an identifiable origin: the document
   title/path plus section, or the repository file plus symbol.
4. Ask only about material decisions that cannot safely be inferred. Batch independent questions
   into one small, prioritized set; do not ask for
   confirmation of established conventions.
5. If a critical decision remains unresolved, publish a clearly marked
   **DRAFT RFC**. Identify the decision, its impact, and the smallest question
   needed to unblock it rather than silently choosing.

## RFC shape

Select only the sections useful for the issue. Scale detail to complexity: a
small feature may need a brief proposal and test notes, while a broad feature
needs explicit boundaries and failure analysis. Draw from this flexible pool:

- status, summary, problem, goals, and non-goals
- context and evidence (including source/claim classifications)
- requirements, constraints, assumptions, and open questions
- proposed design, components, interactions, and data flow
- interfaces and contracts (API, events, storage, or user-visible behavior)
- alternatives and trade-offs
- design risks and delivery risks; keep material design and delivery risks
  separate when relevant
- security, privacy, reliability, observability, and testing
- rollout, migration, compatibility, and rollback
- decision log and unresolved decisions

Explain how components interact and call out relevant interfaces, reliability
behavior, rollout concerns, and trade-offs. Omit irrelevant sections instead
of filling a template mechanically.

## Boundary

An RFC describes the problem and proposes a coherent technical direction. It
must remain separate from file-by-file implementation plans, task batches,
executor assignments, worktrees, estimates, and coding schedules. Those belong
to a later implementation-planning workflow. An RFC may mention likely change
areas or verification needs only when that context helps evaluate the design.
