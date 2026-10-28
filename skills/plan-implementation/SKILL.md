---
name: plan-implementation
description: Use when a task needs a concrete implementation plan with file changes, technical decisions, risks, and test strategy before coding.
---

# When to use
Use for:
- medium or large tasks
- changes crossing multiple layers or modules
- tasks with unclear technical decisions or risk

Do not use for:
- tiny self-evident edits
- pure review tasks after code is already written

# Goal
Produce a concrete implementation plan with no silent assumptions.

# Clarification rule
Do not make assumptions about missing technical details that materially affect implementation.
Ask the user targeted questions before finalizing the plan whenever important details are missing.

Examples of details to clarify when relevant:
- API request and response shape
- authentication and authorization behavior
- validation rules
- idempotency requirements
- concurrency or race-condition constraints
- transaction boundaries
- retry and timeout expectations
- migrations and backward compatibility
- observability requirements
- rollout and failure handling

# Process
1. Restate the goal, confirmed requirements, constraints, non-goals, and
   important decisions.
2. Identify missing details that block a reliable plan.
3. Ask the user targeted questions for those gaps.
4. Propose the smallest viable design consistent with the repository, recording
   the pattern decision defined below.
5. List file-by-file changes.
6. Define test strategy, acceptance evidence, risks, and rollout concerns.

# Pattern decision gate

Record a pattern only when a force exists. When none does, write `none` — an
explicit `none` is a valid and frequent answer.

```text
Pattern decision:
- force: <the concrete pressure this design must absorb>
- response: <pattern or plain structure> + why it is the cheapest answer
- cost / rejected: <what it adds> · <simpler option and why it is insufficient>
```

A force is concrete when it names what breaks without the pattern. Examples:

- two implementations must be selected at runtime;
- I/O crosses a boundary and must be substitutable in tests;
- a dependency must point inward so the domain stays free of transport concerns;
- a concern must apply across call sites without editing each one.

These are not forces: "so it can be extended later", "for separation of
concerns", "cleaner", "more scalable". They select nothing.

- No named force, no pattern.
- At most two patterns. Beyond that the design is too large — split it instead
  of adding structure.
- A pattern the repository does not already use is a deviation. Record it as a
  deviation with the reason; never introduce it silently.
- `cost / rejected` is mandatory. Without it the entry is a preference, not a
  decision.
- If an approved RFC or design document already settles the pattern decision,
  reference it instead of restating it.

The recorded decision is a review criterion: `code-review` checks the code
against it, and a silent divergence is a finding.

# Diagrams

Author the component and sequence diagrams here, while planning — not at PR time.
The plan is the authority a reviewer compares the code against.

- Component: modules and dependency direction, 3 to 12 nodes, one edge per real
  dependency, no class diagrams.
- Sequence: one, for the riskiest flow, including the partial-failure branch, so
  ordering, transaction boundaries, and compensation stay visible.
- Validate that each Mermaid block renders before finalizing the plan.
- Skip diagrams only when the change is localized enough that the file list
  already states the structure.

`open-pr` copies these into the PR body; `code-review` compares the code against
them.

# Rules
- Keep the plan grounded in existing repo patterns.
- Separate confirmed requirements from open questions.
- Preserve relevant requirements, constraints, non-goals, and decisions, and
  explain how the intended behavior will be verified.
- Ground file changes in repository inspection, accounting for files created
  by earlier tasks. Resolve material path mismatches rather than guessing.
- Prefer minimal architecture changes.
- Mark the plan as draft if important questions remain unanswered.

# Output
Provide:
- goal and assumptions confirmed by the user
- relevant requirements, constraints, non-goals, and important decisions
- open questions still pending
- proposed design, including the pattern decision or an explicit `none`
- component and sequence diagrams, unless the change is localized enough to skip them
- file-by-file implementation plan grounded in repository inspection
- test strategy
- risks, migrations, and rollout notes
