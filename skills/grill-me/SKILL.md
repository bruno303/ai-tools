---
name: grill-me
description: Identify only the missing decisions that materially affect implementation. Infer safe defaults from explicit requirements, repository guidance, existing code, tests, contracts, and established project patterns. Ask unresolved questions in small prioritized batches instead of confirming obvious or already-inferable details.
---

# Grill Me

Use this skill when a task, feature, bugfix, refactor, or implementation plan may contain important ambiguities that should be resolved before coding.

The goal is **not** to maximize certainty by asking many questions. The goal is to find the smallest set of unresolved decisions that materially affect implementation.

## Core Principle

Do not ask a question merely because a detail was not explicitly stated.

First determine whether the answer can be safely inferred from available evidence.

Prefer evidence in this order:

1. Explicit task requirements or user instructions.
2. `AGENTS.md` / `CLAUDE.md` and other repository guidance.
3. Existing behavior in the same feature or module.
4. Nearby project patterns and analogous implementations.
5. Existing tests and public contracts.
6. Well-established project conventions.

If the repository already provides a clear answer, use it instead of asking for confirmation.

## Question Classification

Classify each potential ambiguity before asking anything.

### KNOWN

The answer is explicit in the request or repository.

Action: use it. Do not ask.

### SAFE INFERENCE

The answer is not explicitly stated, but project evidence strongly points to one choice and the consequence of being wrong is limited.

Action: infer it, record the assumption briefly if useful, and continue.

### DECISION REQUIRED

Two or more reasonable choices remain and the choice materially affects behavior, architecture, compatibility, persistence, API contracts, rollout, reliability, security, or user-visible semantics.

Action: ask.

## Question Filter

Before asking any question, answer this internally:

> What meaningful implementation decision depends on this answer?

If no meaningful implementation decision depends on it, do not ask.

Also avoid asking when:

- the current codebase already establishes a strong convention;
- the answer can be derived from existing tests or contracts;
- one option is overwhelmingly implied by the task;
- the choice is cosmetic or implementation-local;
- the choice can be safely made and changed later without meaningful cost;
- the question only confirms something already evident from surrounding code.

## Good vs Bad Questions

### Bad: confirming an established convention

> The project currently uses UUIDs for all entity IDs. Should this new entity also use UUIDs?

If there is no evidence that this feature intentionally differs, use UUIDs.

### Good: unresolved API behavior

> Existing endpoints return `409 Conflict` for duplicate resources, but this task only says to "reject duplicates" and this endpoint has no existing duplicate behavior. Should this follow the existing `409` convention, return `422`, or use another contract?

The answer changes externally visible behavior, so asking is justified.

### Bad: asking for obvious implementation details

> Should the new service use dependency injection like the neighboring services?

If the repository consistently uses dependency injection, follow the project pattern.

### Good: compatibility decision

> The schema change can be deployed either backward-compatibly or as a coordinated breaking change. Existing deployments do not establish a precedent for this case. Which rollout model should this change support?

The answer materially changes the implementation and deployment plan.

### Bad: confirming existing error style

> Should errors be wrapped using the project's existing error helper?

If that is the established convention, use it.

### Good: unresolved persistence semantics

> When the same command is received twice, should the operation be idempotent and return the existing result, or should duplicates fail? There is no existing behavior for this command type.

The answer affects persistence, API behavior, and retry safety.

## Batch Questions

Do not interrogate the user one question at a time when several independent decisions can be asked together.

Ask a small prioritized batch, normally **no more than 5-8 questions at once**.

Order questions by impact:

1. Behavioral / product semantics.
2. Public API or contract decisions.
3. Data model and persistence semantics.
4. Compatibility, migration, and rollout.
5. Concurrency, retries, idempotency, and failure handling.
6. Architecture decisions that cannot be inferred from the repository.
7. Lower-risk implementation choices.

Prefer concise multiple-choice options when the realistic alternatives are known.

Example:

```markdown
I found 4 decisions that are not safely inferable from the repository:

1. Duplicate requests
   - A. Return the existing resource
   - B. Return `409 Conflict`
   - C. Other

2. Migration compatibility
   - A. Backward-compatible rollout
   - B. Coordinated breaking deployment

3. Retry semantics
   - A. At-least-once / idempotent handling
   - B. No automatic retry guarantee

4. Existing records
   - A. Backfill during migration
   - B. Migrate lazily when read or updated

Everything else can be inferred from current project patterns.
```

## Avoid Confirmation Theater

Do not ask questions just to make inferred decisions feel explicitly approved.

Bad pattern:

```text
Repository uses PostgreSQL everywhere.
Should this feature also use PostgreSQL?

Repository uses REST for this module.
Should this endpoint use REST?

All sibling handlers return the same error model.
Should this handler use it too?
```

These questions add interaction cost without reducing meaningful uncertainty.

Instead, state only non-obvious assumptions when helpful:

```text
I will follow the module's existing REST and error-handling conventions unless one of the unresolved decisions below changes that assumption.
```

## Missing Definitions vs Missing Confirmation

Prioritize **missing definitions**, not missing confirmations.

Ask when the task does not define something that cannot be safely derived, such as:

- expected behavior when multiple valid outcomes are possible;
- API request/response semantics with no project precedent;
- authorization or security boundaries;
- idempotency requirements;
- retry and timeout expectations;
- ordering guarantees;
- transaction boundaries;
- migration and backward-compatibility requirements;
- conflict resolution behavior;
- failure semantics;
- destructive or irreversible behavior;
- rollout or feature-flag requirements;
- interactions between requirements that appear contradictory.

Do not ask merely because these topics exist. Ask only when they are relevant to the task and unresolved by repository evidence.

## Repository Inspection

Before asking questions, inspect enough repository context to distinguish true ambiguity from already-solved project conventions.

When relevant, check:

- `AGENTS.md` / `CLAUDE.md`;
- analogous features;
- public interfaces and API contracts;
- tests around similar behavior;
- persistence patterns;
- error handling;
- validation rules;
- configuration and rollout conventions.

Do not perform exhaustive repository exploration when a small amount of context is sufficient.

## Contradictions

If two strong sources disagree, do not silently choose one.

Example:

- task says the field is optional;
- API schema marks it required;
- persistence model rejects null values.

This is a real decision gap. Present the conflict clearly and ask which behavior is authoritative.

## Stopping Rule

Stop asking questions when all remaining uncertainty falls into `KNOWN` or `SAFE INFERENCE`.

Do not continue asking for completeness.

If more than roughly 8 high-value questions remain after repository inspection, first check whether:

- several questions can be combined into one decision;
- repository evidence resolves some of them;
- the task is fundamentally underspecified and needs a higher-level product or architecture decision instead of many implementation questions.

## Output Format

When questions are required, use this structure:

```markdown
## What I can infer
- <only important inferred decisions worth surfacing>

## Decisions needed
1. <question>
   - A. ...
   - B. ...

2. <question>
   - A. ...
   - B. ...

## Why these matter
- <brief explanation only when the consequence is not obvious>
```

Omit `What I can infer` when it would only repeat obvious repository behavior.

If no meaningful decisions remain, explicitly say that the task is sufficiently defined and proceed without questions.

## Principles

- Reduce uncertainty, not maximize ceremony.
- Infer from strong project evidence before asking.
- Ask only about decisions with meaningful implementation consequences.
- Prefer a few high-value questions over exhaustive interrogation.
- Batch independent questions.
- Do not ask the user to confirm established project conventions.
- Do not invent requirements when multiple reasonable choices remain.
- Surface contradictions instead of guessing.
- Stop once the task is sufficiently defined to implement safely.
