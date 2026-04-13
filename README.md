# AI-Tools

Reusable agent and skill definitions for agentic software development workflows.

## Repository Overview

- `agents/` contains role-specific agent prompts such as `architect`, `builder`, `spec-driver`, and `reviewer`.
- `skills/` contains reusable guidance modules that agents load when a project matches a language, framework, or workflow.
- `install.sh` installs these agents and skills into another repository.

## Agents

- **`agents/architect.md`** — Orchestrator and planner
  - Coordinates the delivery lifecycle: discovery, planning, implementation, review, and final human approval.
  - Loads shared operating rules plus applicable architecture/framework skills instead of restating common repository-inspection policy inline.
  - Prefers `@explore` for discovery and falls back to a generic read-only exploration subagent when that scout is unavailable, while keeping the same discovery output contract.
  - Requires explicit user approval before execution and enforces strict separation between implementation and review work.

- **`agents/builder.md`** — Implementation subagent
  - Writes production code from an approved task payload.
  - Loads shared operating rules first, then `architectural-guidelines`, plus framework or language skills when applicable.
- Loads `go-architectural_guidelines` for Go projects.
- Loads `nextjs-frontend_guidelines` for Next.js projects.
- Reads only the minimal required context, preserves architecture, avoids unrelated refactors, writes both production code and tests, and reports structured handback output.


- **`agents/spec-driver.md`** — Independent spec-first feature definition agent
  - Converts a feature request into a spec-driven implementation prompt for direct user review before any downstream execution.
  - Loads shared operating rules and applicable architecture/framework skills before drafting repo-aware requirements.
  - Reads current repository behavior before drafting requirements.
  - Requires clarification questions when requirements are ambiguous and avoids assumptions.
  - Runs an internal clarification review loop (up to 5 rounds) to detect ambiguity before returning a final draft.

- **`agents/reviewer.md`** — Senior code reviewer
  - Reviews changed code for correctness, architecture, contract safety, and meaningful maintainability issues.
  - Loads shared operating rules plus applicable architecture/framework skills before reviewing repository code.
  - Loads `go-architectural-guidelines` and `go-testing-guidelines` for Go projects.
  - Loads `nextjs-frontend-guidelines` for Next.js projects.
  - Focuses on reliability and boundary violations rather than style-only feedback.

## Skills

- **`skills/agent-operating-rules/SKILL.md`** — Shared repo-aware operating rules
  - Defines Serena-first repository inspection, minimal-context exploration, source-of-truth lookup, stack detection, shared ambiguity handling, and reusable skill-loading workflow.

- **`skills/architectural-guidelines/SKILL.md`** — Clean Architecture guidance
  - Defines dependency direction, layer responsibilities, repository rules, anti-patterns, testing expectations, and onboarding checks.

- **`skills/go-architectural-guidelines/SKILL.md`** — Go-specific architecture rules
  - Defines Go package layout, dependency injection, entity conventions, delivery rules, error handling, and verification expectations.

- **`skills/go-testing-guidelines/SKILL.md`** — Go-specific testing conventions
  - Defines unit and integration test priorities, isolation rules, naming style, determinism rules, and verification guidance for Go projects.

- **`skills/nextjs-frontend-guidelines/SKILL.md`** — Next.js frontend guidance
  - Defines when the skill applies, the onboarding protocol for Next.js repos, route and file placement rules, server/client boundaries, data-fetching and caching expectations, mutation and form guidance, URL and state rules, testing guidance, anti-patterns, and verification expectations.
  - Intended to be loaded by `@builder` and `@reviewer` when the project is clearly Next.js.

- **`skills/commits/SKILL.md`** — Commit message formatting
  - Defines commit type selection, issue-code prompting rules, and final message format.

## Operating Model

- Production code and tests are always written by `@builder`.
- Planning and approval flow are enforced by `@architect`.
- Agents should load shared operating rules plus architectural, language-specific, and framework-specific skills before making design, implementation, or test decisions.
- Review decisions should use the same framework-specific skills as implementation and test-writing when those skills apply.
- Framework-specific skills are conditional: for example, the Next.js skill should only be loaded when the target repository is clearly a Next.js project.
