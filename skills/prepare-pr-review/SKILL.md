---
name: prepare-pr-review
description: >-
  Prepare a focused human review guide for a pull request or completed code
  change. Use when implementation has already been reviewed or verified and a
  human needs to know where to spend attention. Map risk, critical flows,
  important decisions, reading order, and reviewer questions without duplicating
  a full code review or issuing an approval decision.
---

# Prepare PR Review

Turn a large pull request into a concise map of where human review attention is
most valuable.

This skill is not another code reviewer. It should help a reviewer inspect the
important decisions and execution paths without reading every changed line with
equal depth.

## Goal

Answer:

> Where should a human reviewer spend attention, and what should they verify?

## Use When

Use this skill when:

- a PR or completed change is ready for human review;
- the change is too large to read every line with equal attention;
- normal code review, tests, static analysis, or other verification have already
  covered general correctness and quality;
- the reviewer wants a prioritized reading guide rather than another findings
  report.

Do not use it as a replacement for `code-review`, tests, static analysis, or a
specialized security review.

## Boundary

Do not perform a second full code review.

Do not:

- issue Approve / Request changes decisions;
- exhaustively inspect every changed line;
- repeat style, lint, naming, or generic maintainability comments;
- manufacture findings to appear thorough;
- treat passing checks as proof of semantic correctness;
- claim that low-risk code is guaranteed correct.

If an obvious serious defect appears while preparing the guide, mention it
briefly as a blocking observation, then continue producing the review guide.

## Evidence

Use the strongest available evidence:

1. Task, issue, PR description, RFC, or implementation plan.
2. Changed files and diff.
3. Relevant `AGENTS.md`, `CLAUDE.md`, and repository guidance.
4. Relevant tests and public contracts.
5. Surrounding code needed to understand changed execution paths.
6. Analogous existing code when it clarifies intent or risk.

Inspect only enough repository context to understand the change.

## Process

### 1. Establish expected behavior

Briefly identify:

- what the change is intended to accomplish;
- important behavior that changes;
- invariants or guarantees that matter to review;
- meaningful failure behavior.

Do not restate the whole task.

### 2. Group the change by responsibility

Group changed files into meaningful areas such as:

- domain/application behavior;
- API boundary;
- persistence;
- external integration;
- background processing;
- migration;
- tests;
- configuration;
- generated or mechanical changes.

Prefer behavioral groups over a flat file list.

### 3. Assign review attention

Classify each meaningful group as:

#### HIGH

Review carefully when the area changes things such as:

- business or domain behavior;
- state transitions;
- concurrency, transactions, retries, or idempotency;
- authorization or security boundaries;
- persistence semantics or migrations;
- external contracts;
- meaningful failure handling;
- architecture boundaries or dependency direction;
- non-obvious cross-component behavior.

#### MEDIUM

Read enough to confirm integration and assumptions.

Typical examples:

- ordinary application wiring;
- repository implementation changes following established patterns;
- validation;
- adapters;
- non-trivial configuration;
- tests encoding important behavior.

#### LOW / SKIM

Normally suitable for deliberate skimming instead of line-by-line review.

Typical examples:

- mechanical renames;
- repetitive mappings;
- fixture updates;
- straightforward mocks;
- generated files;
- lockfiles;
- boilerplate following an established pattern.

Always explain the classification. Low risk means lower review priority, not
guaranteed correctness.

### 4. Trace critical flows

Identify the small number of end-to-end paths that best represent the feature.

Example:

```text
HTTP handler
  -> application use case
  -> repository
  -> transaction
  -> event publication
```

Include the changed files or symbols involved. Prioritize boundary crossings and
paths where partial failure could create inconsistent state.

### 5. Surface decisions worth human judgment

Highlight only meaningful decisions the reviewer should consciously validate,
for example:

- responsibility placement;
- transaction or side-effect ordering;
- retry or idempotency semantics;
- API compatibility;
- failure behavior;
- persistence guarantees;
- new abstraction boundaries;
- deviations from existing project patterns.

Do not invent decisions to fill the section.

### 6. Build a reading order

Recommend the smallest useful sequence of files, symbols, or diff ranges.

Example:

```text
1. application/task_runner.go - lifecycle and ordering
2. infra/github/issues.go - selection semantics
3. application/publisher.go - failure handling
4. tests/... - expected edge cases
```

Start with code that establishes behavior, then follow its important
dependencies. Include line ranges when available.

### 7. Prepare reviewer questions

Turn the highest-value assumptions and risks into concrete questions the human
reviewer should be able to answer before merging.

Examples:

- Can two executions select the same work concurrently?
- What happens after a successful side effect followed by a failed write?
- Does validation allow a state downstream code rejects?
- Why does this responsibility belong in this layer?
- Do the tests actually protect the important invariant?

Avoid generic questions such as "Is this code readable?"

## Output

Use this structure and omit empty sections:

### PR review brief

#### What changed
Concise behavioral summary.

#### Invariants and expected behavior
Only guarantees that materially guide review.

#### Attention map
Group areas under `HIGH`, `MEDIUM`, and `LOW / SKIM`, with a reason for
each classification.

#### Critical flows
Show the most important end-to-end paths.

#### Decisions to validate
List meaningful behavior, architecture, reliability, or contract decisions.

#### Suggested reading order
Provide the smallest useful ordered set of files, symbols, or diff ranges.

#### Reviewer questions
Provide a focused set, normally 3-10 depending on change size.

#### Blocking observation
Include only when an obvious serious defect or requirement conflict appeared
while preparing the guide.

## Principles

- Allocate attention instead of maximizing review coverage.
- Prefer behavior and decisions over file count.
- Treat risk as contextual, not as a numeric score.
- Explain why an area deserves deep review or only a skim.
- Keep the guide substantially smaller than the diff.
- Use repository evidence rather than generic best practices.
- Distinguish facts from assumptions.
- Do not duplicate `code-review`.
- Do not issue an approval decision.
