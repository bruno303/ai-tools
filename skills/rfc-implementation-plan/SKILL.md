---
name: rfc-implementation-plan
description: Use when an approved or mostly-final RFC must become an implementation-ready plan grounded in repository evidence, with sized tasks, dependencies, validation, and only material clarification questions.
---

# RFC Implementation Plan

## When to use

Use this skill when an RFC is approved or mostly final and its decisions need
to be translated into an implementation-ready plan. It is a bridge between a
design decision and the execution workflow.

Do not use it to draft, redesign, or approve an RFC; to make a general plan
when no RFC exists; or to execute an already-written plan. This skill stops
after producing the plan. The plan should work with the harness's normal
implementation flow and remain compatible with `subagent-plan-execution` when
that heavier workflow is explicitly invoked.

## Evidence and RFC extraction

Inspect the RFC first and extract, without reopening settled design choices:

- goals and non-goals;
- constraints and explicit decisions;
- the selected design and affected interfaces;
- compatibility, migration, rollout, and operational requirements; and
- implementation-relevant acceptance criteria.

Resolve evidence in this order:

1. explicit RFC decisions and constraints;
2. repository guidance and contracts (`AGENTS.md`, `CLAUDE.md`, schemas, and
   documented workflows);
3. current code and tests;
4. nearby patterns; and
5. low-risk inference.

Record conflicts rather than silently choosing between strong sources.

## Repository inspection

Inspect the affected modules and their boundaries before sizing work. Include,
as applicable, abstractions and implementations, integration points and
callers, related tests, configuration, migrations and persistence,
infrastructure, deployment/rollout, and observability or other operational
concerns. Follow existing dependency direction and patterns. The plan should
name repository areas, not merely list guessed files.

For unfamiliar or non-trivial reconnaissance, use `analyze-codebase`; keep
direct reads preferred for small, already-localized checks. Shared
reconnaissance may use that skill's optional delegation, but this workflow
remains planning-only and does not orchestrate implementation workers.

Classify each finding as one of:

- **RFC-settled** — decided by the RFC;
- **repository-derived detail** — established by code, tests, contracts, or
  project conventions;
- **RFC/repository contradiction** — strong evidence disagrees; or
- **missing implementation-critical decision** — inspection cannot safely
  determine an outcome that materially affects implementation.

Inspect before asking. Infer safe, low-risk details and state important
assumptions briefly. Batch only material clarification questions, prioritizing
behavior, public contracts, persistence, compatibility/rollout, and failure
semantics. Do not ask for confirmation of established conventions.

## Task decomposition and dependencies

Group work by cohesive outcome rather than by file. Keep a small RFC as one
task. Split only when there is a real dependency boundary, independent
ownership, materially different risk, or meaningful validation boundary. Avoid
file-level microtasks.

Record dependencies explicitly. Default to serial execution. Mark tasks
parallel-safe only when there is no dependency path and no conflicting
repository scope. Worktrees and dispatch are execution concerns, not
responsibilities of this skill.

Every task must have an objective, repository area, expected changes/scope,
dependencies, and task-level validation. List known files and expected new,
deleted, or renamed artifacts when repository inspection identifies them with
confidence, but do not require an exhaustive exact-path allowlist and do not
guess filenames just to make the plan look concrete. Describe remaining scope
using modules, directories, interfaces, or boundaries.

If `subagent-plan-execution` is explicitly invoked later, its existing
pre-dispatch normalization step owns the exact writable path allowlist and may
resolve clearly necessary supporting paths from this plan. That is execution
preparation, not another design/planning pass.

Include final integration validation for the complete change.

## Output

Produce a concise, writable plan with this shape:

```markdown
# Implementation plan: <RFC>

## Implementation summary
- <selected behavior and important RFC decisions>

## Affected areas
- <modules, boundaries, configuration, data, infrastructure, operations>

## Assumptions and blockers
- <repository-derived assumptions>
- <material blockers or “none”>

## Ordered tasks
### Task 1: <cohesive outcome>
- **Objective:** <observable result>
- **Repository area:** <paths/modules and boundaries>
- **Expected changes/scope:** <implementation behavior, interfaces, and tests>
- **Known files/artifacts:** <known paths and operations when confidently identified; otherwise omit>
- **Dependencies:** <none or task IDs>
- **Validation:** <focused checks and acceptance criteria>

## Execution notes
- <serial/parallel rationale and constraints for the execution workflow>

## Final integration and validation
- <cross-task checks, rollout/migration checks, and final test command>
```

The plan must contain enough concrete repository scope and acceptance-oriented
validation to start implementation without another design pass. Exact worker
allowlists, worktrees, and dispatch details remain execution concerns. See
[references/examples.md](references/examples.md).

## Boundaries

This skill only inspects, resolves material ambiguity, and writes the plan. It
must not implement code, run tests or other verification, perform code review,
manage worktrees, or orchestrate implementation-worker dispatch. Shared
repository reconnaissance may still follow `analyze-codebase` when needed.
