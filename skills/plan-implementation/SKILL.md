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
4. Propose the smallest viable design consistent with the repository.
5. List file-by-file changes.
6. Define test strategy, acceptance evidence, risks, and rollout concerns.

# Rules
- Keep the plan grounded in existing repo patterns.
- Separate confirmed requirements from open questions.
- Record confirmed requirements, constraints, non-goals, and important
  decisions explicitly, including negative constraints and defaults that affect
  behavior, each with the acceptance evidence that shows it is met.
- Resolve expected output paths against the repository: name the exact existing
  path for an edit; for a new path, confirm its parent and that its location and
  naming follow repository and test-placement conventions. Do not list a path
  that has not been checked.
- Prefer minimal architecture changes.
- Mark the plan as draft if important questions remain unanswered.

# Output
Provide:
- goal and assumptions confirmed by the user
- confirmed requirements, constraints, non-goals, and important decisions with
  acceptance evidence
- open questions still pending
- proposed design
- file-by-file implementation plan with repository-resolved paths
- test strategy
- risks, migrations, and rollout notes
