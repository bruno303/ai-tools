# AI-Tools

Reusable agent and skill definitions for agentic software development workflows.

## Repository Overview

- `agents/` contains role-specific agent prompts such as `architect`, `builder`, `test-writer`, and `reviewer`.
- `skills/` contains reusable guidance modules that agents load when a project matches a language, framework, or workflow.
- `install.sh` installs these agents and skills into another repository.

## Agents

- **`agents/architect.md`** — Orchestrator and planner
  - Coordinates the delivery lifecycle: discovery, planning, implementation delegation, test-writing delegation, review, and final human approval.
  - Requires explicit user approval before execution and enforces strict separation between production code, tests, and review work.

- **`agents/builder.md`** — Implementation subagent
  - Writes production code from an approved task payload.
  - Loads `architectural-guidelines` first, plus framework or language skills when applicable.
  - Loads `go-architectural-guidelines` for Go projects.
  - Loads `nextjs-frontend-guidelines` for Next.js projects.
  - Reads only the minimal required context, preserves architecture, avoids unrelated refactors, does not write tests, and reports structured handback output.

- **`agents/test-writer.md`** — Test writer subagent
  - Writes and verifies tests for code produced by the builder.
  - Loads `architectural-guidelines` and `testing-guidelines` first, plus framework or language skills when applicable.
  - Loads `go-architectural-guidelines` for Go projects.
  - Loads `nextjs-frontend-guidelines` for Next.js projects so coverage follows framework-specific boundaries and behavior expectations.
  - Must not change production code and returns structured test results, bugs found, and blockers.

- **`agents/reviewer.md`** — Senior code reviewer
  - Reviews changed code for correctness, architecture, contract safety, and meaningful maintainability issues.
  - Loads framework or language skills when applicable, including `nextjs-frontend-guidelines` for Next.js projects.
  - Focuses on reliability and boundary violations rather than style-only feedback.

## Skills

- **`skills/architectural-guidelines/SKILL.md`** — Clean Architecture guidance
  - Defines dependency direction, layer responsibilities, repository rules, anti-patterns, testing expectations, and onboarding checks.

- **`skills/go-architectural-guidelines/SKILL.md`** — Go-specific architecture rules
  - Defines Go package layout, dependency injection, entity conventions, delivery rules, error handling, and verification expectations.

- **`skills/go-testing-guidelines/SKILL.md`** — Go-specific testing conventions
  - Defines unit and integration test priorities, isolation rules, naming style, determinism rules, and verification guidance for Go projects.

- **`skills/nextjs-frontend-guidelines/SKILL.md`** — Next.js frontend guidance
  - Defines when the skill applies, the onboarding protocol for Next.js repos, route and file placement rules, server/client boundaries, data-fetching and caching expectations, mutation and form guidance, URL and state rules, testing guidance, anti-patterns, and verification expectations.
  - Intended to be loaded by `@builder`, `@test-writer`, and `@reviewer` when the project is clearly Next.js.

- **`skills/commits/SKILL.md`** — Commit message formatting
  - Defines commit type selection, issue-code prompting rules, and final message format.

## Operating Model

- Production code is always written by `@builder`.
- Test code is always written by `@test-writer`.
- Planning and approval flow are enforced by `@architect`.
- Agents should load architectural, language-specific, and framework-specific skills before making design, implementation, or test decisions.
- Review decisions should use the same framework-specific skills as implementation and test-writing when those skills apply.
- Framework-specific skills are conditional: for example, the Next.js skill should only be loaded when the target repository is clearly a Next.js project.
