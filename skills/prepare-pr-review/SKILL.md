---
name: prepare-pr-review
description: >-
  Prepare a focused human review guide for a pull request or completed code
  change. Use when the implementation has already been reviewed or verified and
  a human reviewer needs to know where to spend attention. Map risk, critical
  flows, important decisions, suggested reading order, and reviewer questions
  without duplicating a full code review or issuing an approval decision.
---

# Prepare PR Review

Turn a large pull request or completed change into a concise map of where human
review attention is most valuable.

This skill is not another code reviewer. Its job is to reduce the amount of code
a human must read line-by-line while preserving attention on the decisions and
execution paths most likely to matter.

## Goal

Answer:

> Where should a human reviewer spend attention, and what should they verify?

The output should let a reviewer understand the change, inspect the highest-risk
parts first, and deliberately skim low-risk or mechanical parts.

## Use When

Use this skill when:

- a pull request is ready for human review;
- the change is too large to read every line with equal attention;
- automated checks or another review step have already handled general code
  quality and correctness;
- the reviewer wants a prioritized reading guide instead of another list of
  findings.

Do not use this skill as a replacement for:

- `code-review`;
- tests, static analysis, or other verification;
- security review when the change requires one;
- understanding an implementation that is still actively being designed.

## Core Boundary

Do not perform a second full code review.

Specifically, do not:

- produce an Approve / Request changes decision;
- manufacture findings;
- repeat lint, style, naming, or generic maintainability comments;
- exhaustively inspect every changed line;
- claim that low-risk code is guaranteed correct;
- treat test or static-analysis success as proof of semantic correctness.

If a serious defect becomes obvious while preparing the guide, surface it
briefly as a blocking observation rather than hiding it, but do not turn the
rest of the output into a normal code review.

## Evidence to Gather

Start with the strongest available evidence:

1. Task, issue, PR description, RFC, or implementation plan.
2. Changed files and diff.
3. `AGENTS.md`, `CLAUDE.md`, and relevant repository guidance.
4. Relevant tests and public contracts.
5. Surrounding code needed to understand changed execution paths.
6. Existing analogous code when it clarifies risk or intent.

Do not explore the repository broadly without a concrete reason.

If requirements and implementation evidence conflict, call out the conflict as
something the human reviewer must resolve.

## Process

### 1. Establish Expected Behavior

Briefly derive:

- what the change is intended to accomplish;
- externally visible or domain-visible behavior that changes;
- important invariants or guarantees;
- important failure behavior, when relevant.

Keep this short. The purpose is to create a review lens, not restate the entire
task.

### 2. Partition the Change by Responsibility

Group changed files by meaningful responsibility or flow rather than listing
every file independently.

Examples:

- domain and application behavior;
- HTTP or RPC boundary;
- persistence;
- external integration;
- background processing;
- migration;
- tests;
- configuration;
- generated or mechanical changes.

Prefer groups that help a reviewer reason about behavior.

### 3. Assign Review Attention

Classify each meaningful group as:

#### HIGH

Human review should inspect this carefully.

Typical reasons include:

- business or domain behavior changes;
- state transitions;
- concurrency, transactions, retries, or idempotency;
- authorization or security boundaries;
- persistence semantics or migrations;
- external contracts;
- failure handling with meaningful production impact;
- architectural boundaries or dependency direction;
- non-obvious cross-component behavior.

#### MEDIUM

Read enough to confirm integration and assumptions.

Typical examples include:

- ordinary application wiring;
- repository implementation changes with established patterns;
- validation;
- adapters;
- non-trivial configuration;
- tests encoding important behavior.

#### LOW / SKIM

Normally suitable for deliberate skimming rather than line-by-line review.

Typical examples include:

- mechanical renames;
- repetitive mappings;
- fixture updates;
- straightforward mocks;
- generated files;
- lockfiles;
- boilerplate following an established pattern.

Always explain why something is low risk. Never use the classification as a
guarantee that the code cannot contain defects.

### 4. Trace Critical Flows

Identify the small number of end-to-end flows that best represent the feature.

For each flow, show the relevant path, for example:

```text
HTTP handler
  -> application use case
  -> repository
  -> transaction
  -> event publication
```

Mention the changed files or symbols involved.

Prioritize flows where behavior crosses boundaries or where partial failure can
create inconsistent state.

### 5. Identify Decisions Worth Human Judgment

Surface design or behavioral decisions a human reviewer should consciously
validate, such as:

- why a responsibility lives in a particular layer;
- transaction or side-effect ordering;
- retry semantics;
- API compatibility;
- failure behavior;
- persistence guarantees;
- newly introduced abstraction boundaries;
- deviations from existing project patterns.

Do not invent decisions just to fill the section.

### 6. Build a Reading Order

Recommend a short review sequence.

Start with the files or symbols that establish behavior, then follow the most
important dependencies.

Prefer:

```text
1. application/task_runner.go - lifecycle and ordering
2. infra/github/issues.go - selection semantics
3. application/publisher.go - failure handling
4. tests/... - expected edge cases
```

over a raw list of every changed file.

When line ranges are available, include them.

### 7. Prepare Reviewer Questions

Turn the highest-value uncertainties into concrete questions the reviewer should
be able to answer before merging.

Good questions challenge assumptions or connect multiple parts of the change:

- Can two executions select the same work concurrently?
- What happens after a successful external side effect followed by a failed
  persistence update?
- Does validation allow a state that downstream code rejects?
- Why does this responsibility belong in this layer?
- Does the test suite actually protect the invariant described by the task?

Avoid generic questions such as "Is this code readable?"

## Output Format

Use this structure and omit empty sections.

### PR review brief

#### What changed
A concise behavioral summary.

#### Invariants and expected behavior
Only the guarantees that materially guide review.

#### Attention map
Group code by `HIGH`, `MEDIUM`, and `LOW / SKIM`, with a short reason for
each classification.

#### Critical flows
Show the most important end-to-end paths through the change.

#### Decisions to validate
List only meaningful architecture, behavior, reliability, or contract decisions.

#### Suggested reading order
Provide the smallest useful ordered set of files, symbols, or diff ranges.

#### Reviewer questions
Provide a focused set of questions, normally 3-10 depending on change size.

#### Blocking observation
Include only when an obvious serious defect or requirement conflict was
encountered while preparing the guide.

## Principles

- Allocate attention instead of maximizing review coverage.
- Prefer behavior and decisions over file count.
- Treat risk as contextual, not as a numeric score.
- Explain why an area deserves deep review or only a skim.
- Keep the guide substantially smaller than the diff it describes.
- Use repository evidence rather than generic best practices.
- Distinguish facts from assumptions.
- Do not duplicate `code-review`.
- Do not issue an approval decision.
- A useful result may intentionally tell the reviewer to deeply read only a
  small fraction of the changed lines.
