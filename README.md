# AI-Tools

Reusable agent and skill definitions for agentic software development workflows.

## Repository Overview

- `opencode/agents/`, `codex/agents/`, and `claude/agents/` contain the active `executor` and `reviewer` roles in each harness's native format.
- `archive/opencode/agents/` preserves the retired `architect`, `builder`, `reviewer`, and `spec-driver` definitions for reference; archived files are not installed.
- `skills/` contains reusable skills shared across agents.
- `benchmarks/` contains a harness-agnostic runner and repeatable scenarios for comparing models, skills, and workflows.

## Agents

Each harness ships two model-only profiles:

- **`executor`** selects the implementation model.
- **`reviewer`** selects the review model.

The active agent files intentionally contain no behavioral prompt, handback schema, or workflow instructions. Skills provide those instructions and coordinate how the main agent uses each profile.

The former `architect`, `builder`, and `spec-driver` orchestration roles, along with the prior reviewer prompt, are archived under `archive/opencode/agents/`.

Model assignments are native to each harness: OpenCode uses `opencode/gpt-5.6-luna` for the executor and `opencode/gpt-5.6-sol` for the reviewer; Codex uses `gpt-5.6-luna` and `gpt-5.6-sol`; Claude uses `haiku` and `sonnet`. Customize model and, where supported, reasoning-effort fields in the corresponding files under `opencode/agents/`, `codex/agents/`, or `claude/agents/`.

## Skills

- **`skills/analyze-codebase/SKILL.md`** - map relevant files, call flow, boundaries, and patterns before edits.
- **`skills/write-rfc/SKILL.md`** - turn requirements and repository evidence into a proportional RFC, clarifying only material decisions before planning.
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
- **`skills/simplify/SKILL.md`** - refine recently modified code for clarity and consistency without changing functionality.
- **`skills/subagent-plan-execution/SKILL.md`** - execute an existing implementation plan with lightweight task gates, one final aggregate code review, bounded fix passes, and non-looping quality gates.
- **`skills/grill-me/SKILL.md`** - identify only implementation-relevant ambiguities, infer safe defaults from the repository, and batch unresolved decisions instead of asking confirmation-only questions.
- **`skills/init-agents-md/SKILL.md`** - create or update the root `AGENTS.md` with workflows, commands, architecture, and agent working rules.

## Benchmarks

The benchmark runner compares coding-agent setups against the same isolated scenario and deterministic evaluators. A variant is just a command plus optional setup/environment, so OpenCode, Codex, Claude Code, custom orchestrators, different models, and different skill sets can all be compared without coupling the benchmark to a specific harness.

```bash
python3 benchmarks/benchmark.py run \
  benchmarks/scenarios/normalize-username/scenario.json \
  benchmarks/scenarios/deactivate-user \
  benchmarks/variants/opencode.example.json
```

Runs persist independent JSON results with success, verification output, and wall-clock time. Optional harness-exported token/call metrics are also preserved. Pass multiple scenario files or directories before the final variant path; use `--repeat` for nondeterministic sampling, `--verbose` for live agent output, `--quiet` to suppress heartbeats and streaming, and `--results-dir DIR` to redirect result files. Use `benchmark.py compare` to aggregate each scenario/variant pair, with optional `--scenario NAME` and `--variant NAME` filters.

See `benchmarks/README.md` for the detailed runner, scenario, and variant guide.

## Installation

Install the active pair for one harness into a target repository:

```bash
./install-agents.sh <opencode|codex|claude> <target-dir>
./install-agents.sh --clean <opencode|codex|claude> <target-dir>
```

Destinations are `<target>/agents` for OpenCode, `<target>/.codex/agents` for Codex, and `<target>/.claude/agents` for Claude. `--clean` removes only the selected harness's agent directory. The compatibility command `opencode/install.sh [--clean] [--remove-model] <target-dir>` remains available for OpenCode's existing workflow.

Install the skills from this repo globally (no clone required):

```bash
npx skills add https://github.com/bruno303/ai-tools --skill "*"
```

Or run `install-skils.sh`, which also installs external skills (`using-git-worktrees`, `skill-creator`, `caveman`):

```bash
./install-skils.sh
```

## Operating Model

- The main agent/orchestrator and skills own discovery, planning, approval, coordination, and final integration.
- `subagent-plan-execution` dispatches implementation and fix workers through the `executor` profile and review workers through the `reviewer` profile; those profiles own model selection while the skill owns behavior.
- Select the native model profile needed by the coordinating skill; the archived legacy definitions are not part of the active installation.
- Skills are loaded as needed based on task type (analysis, planning, API/DB changes, verification, review, debugging, language conventions).
