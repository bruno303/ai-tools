---
name: code-review
description: >-
  Perform a senior-level code review of a feature or code change, focusing on
  correctness, reliability, readability, maintainability, feature coherence,
  tests, and consistency with the project's architecture, patterns, structure,
  and conventions. Use AGENTS.md or CLAUDE.md and nearby repository code as the project
  baseline. Avoid low-value nitpicks and report only actionable, evidence-backed
  findings.
---

# Code Review

Perform a high-quality code review as an experienced senior software engineer.

The review must evaluate the change in the context of the entire feature and the
existing project, not only as isolated code or a diff.

## Objectives

Determine:

1. What the feature or change is trying to accomplish.
2. Whether the implementation actually accomplishes it.
3. Whether it introduces bugs, edge cases, reliability problems, regressions,
   or invalid behavior.
4. Whether the code is easy for another engineer to understand and maintain.
5. Whether all parts of the feature agree on the same behavior.
6. Whether the change follows the project's architecture, patterns, structure,
   and conventions.
7. Whether tests adequately protect the intended behavior.

Prioritize meaningful engineering problems over stylistic preferences.

---

# Review Workflow

## 1. Understand the Change

Before judging the implementation:

- Identify the purpose of the feature.
- Identify the user-visible, domain, API, persistence, integration, or internal
  behavior being changed.
- Inspect the changed files.
- Inspect enough surrounding code to understand how the feature fits into the
  existing system.
- Inspect callers, dependencies, interfaces, domain models, and tests when they
  materially affect the behavior.

Do not assume requirements that are unsupported by the repository context.

If the intended behavior is ambiguous, infer it from the strongest available
evidence in this order:

1. Explicit requirements or task description.
2. Tests.
3. Public interfaces and API contracts.
4. Domain models and invariants.
5. Existing project behavior and patterns.
6. Relevant documentation.

If two sources conflict, report the conflict instead of silently choosing one.

## 2. Read Project Guidance

Read the project's `AGENTS.md` or `CLAUDE.md`.

If both exist, read both and combine the relevant guidance. If they conflict, prefer the more specific instruction for the affected area and explicitly note any unresolved conflict.

Extract only the parts relevant to the code being reviewed.

Focus on:

- architecture
- module boundaries
- directory and package structure
- dependency direction
- naming conventions
- error-handling conventions
- testing conventions
- logging and observability
- configuration patterns
- persistence patterns
- domain modeling
- integration patterns
- repository-specific rules

Do not repeat or load unrelated guidance into the review.

Treat explicit repository rules as stronger evidence than generic industry best
practices.

## 3. Inspect Existing Patterns

When relevant, find similar code already present in the project.

Use existing implementations to understand:

- how similar features are structured
- where responsibilities normally live
- how dependencies are introduced
- how errors are represented and propagated
- how transactions are handled
- how integrations are wrapped
- how tests are organized
- how domain behavior is modeled

Prefer established project patterns unless the new implementation has a clear,
defensible reason to differ.

Do not flag a difference merely because another design is possible.

---

# Review Dimensions

## Correctness

Check whether the implementation performs the intended behavior correctly.

Look for:

- incorrect logic
- invalid assumptions
- missing cases
- invalid state transitions
- wrong return values
- incorrect conditionals
- incorrect data transformations
- broken error propagation
- incorrect API behavior
- inconsistent behavior between related code paths
- races or concurrency bugs
- regression risks
- behavior that contradicts tests, contracts, or requirements

Prioritize problems that can cause incorrect runtime behavior.

## Reliability

Evaluate behavior under realistic failure conditions.

Consider, when relevant:

- retries
- timeouts
- partial failures
- concurrency
- idempotency
- transaction boundaries
- resource cleanup
- network failures
- database failures
- duplicate requests or events
- malformed input
- missing data
- external service failures
- error propagation
- graceful degradation
- cancellation
- ordering guarantees
- consistency between writes and side effects

Do not invent extremely hypothetical failure modes that are not meaningful for
the application.

## Readability and Maintainability

The implementation should be easy for an engineer familiar with the project to
understand.

Check for:

- unclear naming
- unnecessary complexity
- deeply nested logic
- hidden side effects
- confusing control flow
- duplicated logic
- mixed responsibilities
- abstractions that obscure rather than simplify behavior
- functions, methods, or classes doing too many unrelated things
- code whose intent cannot be understood without excessive context
- unnecessary indirection
- inconsistent terminology for the same domain concept

Prefer simple, explicit, project-consistent solutions.

Do not recommend abstractions merely for the sake of abstraction.

Do not report subjective style preferences unless they materially affect
readability or violate an established project convention.

## Feature Coherence

Review the feature as a whole.

Determine whether:

- all components agree on the intended behavior
- API, domain, persistence, integrations, and tests describe the same behavior
- different parts of the change make conflicting assumptions
- one code path contradicts another
- validation agrees with downstream requirements
- naming matches actual behavior
- persistence semantics agree with business logic
- the feature creates impossible or contradictory states
- the implementation works end-to-end

Explicitly look for conflicts such as:

- one component treating a value as optional while another requires it
- validation accepting a state downstream code cannot process
- an API contract promising behavior the domain layer does not implement
- persistence semantics conflicting with domain rules
- tests encoding behavior different from the implementation
- two execution paths implementing the same feature differently

When reporting a conflict, identify both sides and explain why they cannot both
be correct.

## Project Consistency

Compare the implementation with the project's established patterns.

Check whether it respects:

- architecture
- module boundaries
- package and directory organization
- dependency direction
- naming conventions
- error handling
- logging
- observability
- testing patterns
- configuration patterns
- persistence patterns
- domain modeling conventions
- integration conventions

Flag inconsistencies when they:

- violate explicit repository rules
- break architectural boundaries
- introduce a materially different pattern without justification
- increase maintenance cost
- make similar code behave inconsistently
- create unnecessary conceptual duplication

When reporting such an issue, reference the relevant `AGENTS.md` or `CLAUDE.md` guidance or
existing project pattern that establishes the expected approach.

## Tests

Evaluate whether tests adequately protect the introduced behavior.

Look for:

- important behavior without coverage
- missing failure scenarios
- missing boundary conditions
- missing regression tests for fixed bugs
- tests that only assert implementation details
- tests too weak to catch realistic regressions
- tests contradicting the intended feature behavior
- tests inconsistent with project conventions
- happy-path-only coverage where failure handling is part of the feature

Do not request tests for trivial implementation details that add little value.

---

# Low-Value Comment Filter

Do not produce comments merely because:

- the code could be written differently
- another abstraction might be more elegant
- a naming choice is slightly subjective
- formatting could be different
- a micro-optimization exists
- an extremely hypothetical edge case exists
- a different design is personally preferable
- a generic best practice differs from the project's established convention

Before reporting a finding, ask:

> What realistic problem does this cause?

If there is no meaningful answer, do not report it.

Every finding must be:

- concrete
- actionable
- supported by evidence
- relevant to correctness, reliability, maintainability, coherence, tests, or
  project consistency

Do not manufacture findings to make the review appear thorough.

A clean review is a valid result.

---

# Severity

Use the following severity levels.

## Critical

Use when the issue is likely to cause:

- data loss
- serious security vulnerability
- severe production failure
- unrecoverable corruption
- a fundamentally broken feature

## High

Use for:

- significant correctness bugs
- substantial reliability issues
- likely regressions
- broken core behavior
- serious architectural violations
- failures affecting common or important execution paths

## Medium

Use for:

- meaningful edge-case bugs
- maintainability problems with concrete future cost
- inconsistencies with project patterns
- incomplete failure handling
- test gaps around important behavior
- feature contradictions with limited immediate impact

## Low

Use only for legitimate, limited-impact improvements that still have a concrete
engineering benefit.

Do not inflate severity.

---

# Finding Format

For every issue, use this structure:

## [Severity] Short finding title

**Location:**  
File and relevant function, class, method, or line when possible.

**Problem:**  
Explain precisely what is wrong.

**Why it matters:**  
Describe the realistic consequence.

**Evidence:**  
Reference the relevant code, project pattern, `AGENTS.md`/`CLAUDE.md` rule, test, contract,
or conflicting behavior.

**Suggested direction:**  
Describe how the issue could be addressed without unnecessarily prescribing an
exact implementation.

For feature conflicts, explicitly describe the two conflicting assumptions or
behaviors.

---

# Final Review Output

Structure the final review as follows.

## Feature understanding

Briefly explain what the feature appears intended to do.

Do not over-explain implementation details.

## Project patterns considered

Summarize only the relevant project architecture, patterns, and conventions used
as review criteria.

Mention the relevant `AGENTS.md` or `CLAUDE.md` guidance and existing code patterns when useful.

## Findings

List findings ordered by severity:

1. Critical
2. High
3. Medium
4. Low

Within the same severity, order by likely impact.

Do not create findings to fill this section.

If no meaningful issues are found, explicitly state:

> No blocking or meaningful code quality issues found.

## Overall assessment

Choose exactly one:

- **Approve**
- **Approve with minor concerns**
- **Changes requested**
- **Major redesign required**

Use:

- **Approve** when there are no meaningful issues.
- **Approve with minor concerns** when only low-impact issues remain.
- **Changes requested** when one or more issues should be fixed before merge.
- **Major redesign required** when the approach is fundamentally incompatible
  with the feature requirements or project architecture.

Briefly explain the decision.

---

# Review Principles

Always follow these principles:

- Review behavior before style.
- Prefer correctness over elegance.
- Prefer reliability over cleverness.
- Prefer readability over unnecessary abstraction.
- Prefer existing project conventions over generic best practices.
- Evaluate the feature end-to-end.
- Look for contradictions between different parts of the implementation.
- Distinguish actual defects from optional improvements.
- Do not assume missing requirements without repository evidence.
- Do not review only the diff when surrounding context is needed.
- Do not make speculative claims without evidence.
- Do not generate findings just to appear thorough.
- Every reported issue must be defensible to the engineer who wrote the code.
- When uncertain whether something is a defect or merely a preference, omit it
  unless repository evidence makes the issue concrete.
