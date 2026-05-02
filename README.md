# AI-Tools

Reusable agent and skill definitions for agentic software development workflows.

## Repository Overview

- `opencode/agents/` contains OpenCode agent prompts (`architect`, `builder`, `spec-driver`, `reviewer`) in Markdown.
- `codex/agents/` contains Codex equivalents of the same agents in TOML.
- `skills/` contains reusable skills shared across agents.
- `opencode/install.sh` installs OpenCode `agents/` and `skills/` into another repository.

## Agents

The same four agents are defined for both runtimes:

- **`architect`** (`opencode/agents/architect.md`, `codex/agents/architect.toml`)
  - Orchestrates delivery as: discover -> plan -> build -> optional review -> human approval.
  - Delegates implementation to `builder` and requires explicit `Approve` before execution.

- **`builder`** (`opencode/agents/builder.md`, `codex/agents/builder.toml`)
  - Implementation subagent that writes production code and tests from approved tasks.
  - Uses a strict handback format with verification results and blockers.

- **`reviewer`** (`opencode/agents/reviewer.md`, `codex/agents/reviewer.toml`)
  - Read-only senior reviewer focused on correctness, contracts, coverage, reliability, and architecture.
  - Reports evidence-based findings with severity and fix direction.

- **`spec-driver`** (`opencode/agents/spec-driver.md`, `codex/agents/spec-driver.toml`)
  - Spec-first agent that turns feature requests into implementation-ready specification drafts.
  - Requires clarification for ambiguity and can return `DRAFT READY` or `BLOCKED`.

## Skills

- **`skills/analyze-codebase/SKILL.md`** - map relevant files, call flow, boundaries, and patterns before edits.
- **`skills/plan-implementation/SKILL.md`** - create a concrete implementation plan, including risks and test strategy.
- **`skills/write-tests/SKILL.md`** - add or update behavior-focused tests at the right level.
- **`skills/run-verification/SKILL.md`** - run the smallest relevant checks first, then expand as needed.
- **`skills/review-changes/SKILL.md`** - review changed code for correctness, regressions, architecture fit, and missing tests.
- **`skills/debug-failure/SKILL.md`** - isolate likely root cause for failing tests, builds, CI, or runtime behavior.
- **`skills/api-change-checklist/SKILL.md`** - checklist for API or contract changes.
- **`skills/db-change-checklist/SKILL.md`** - checklist for schema, query, migration, and rollout risk.
- **`skills/observability-instrumentation-check/SKILL.md`** - ensure logs/metrics/traces/alerts are actionable and low-noise.
- **`skills/project-coding-guidelines/SKILL.md`** - enforce repository-first architecture and placement conventions before implementation.
- **`skills/go-coding/SKILL.md`** - Go coding conventions for readability, maintainability, and correctness.

## Operating Model

- `architect` coordinates planning and approval gates.
- `builder` owns production code changes and tests.
- `reviewer` performs scoped, read-only quality review.
- `spec-driver` is the spec-first path when requirements need to be formalized before coding.
- Skills are loaded as needed based on task type (analysis, planning, API/DB changes, verification, review, debugging, language conventions).
