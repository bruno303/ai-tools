# AI-Tools

Reusable agent and skill definitions for agentic software development workflows.

## Repository Overview

- `opencode/agents/` contains OpenCode agent prompts (`architect`, `builder`, `spec-driver`, `reviewer`) in Markdown.
- `skills/` contains reusable skills shared across agents.

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
- **`skills/code-review/SKILL.md`** - review code for correctness, regressions, architecture fit, and missing tests.
- **`skills/debug-failure/SKILL.md`** - isolate likely root cause for failing tests, builds, CI, or runtime behavior.
- **`skills/api-change-checklist/SKILL.md`** - checklist for API or contract changes.
- **`skills/db-change-checklist/SKILL.md`** - checklist for schema, query, migration, and rollout risk.
- **`skills/observability-instrumentation-check/SKILL.md`** - ensure logs/metrics/traces/alerts are actionable and low-noise.
- **`skills/project-coding-guidelines/SKILL.md`** - enforce repository-first architecture and placement conventions before implementation.
- **`skills/go-expert/SKILL.md`** - idiomatic, production-grade Go coding conventions.
- **`skills/nextjs-coding/SKILL.md`** - Next.js frontend conventions for readability, maintainability, and correctness.
- **`skills/subagent-plan-execution/SKILL.md`** - execute an existing implementation plan by dispatching fresh subagents per task.
- **`skills/init-agents-md/SKILL.md`** - create or update the root `AGENTS.md` with workflows, commands, architecture, and agent working rules.

## Installation

Install the skills from this repo globally (no clone required):

```bash
npx skills add https://github.com/bruno303/ai-tools --global --yes
```

Or run `install-skils.sh`, which also installs external skills (`using-git-worktrees`, `skill-creator`, `grill-me`, `caveman`):

```bash
./install-skils.sh
```

## Operating Model

- `architect` coordinates planning and approval gates.
- `builder` owns production code changes and tests.
- `reviewer` performs scoped, read-only quality review.
- `spec-driver` is the spec-first path when requirements need to be formalized before coding.
- Skills are loaded as needed based on task type (analysis, planning, API/DB changes, verification, review, debugging, language conventions).
