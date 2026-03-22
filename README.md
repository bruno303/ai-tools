# AI-Tools

Contains AI configurations like agents, skills and commands.

## Agents

- **`agents/architect.md`** — Orchestrator & Planner
  - Role: Lead feature lifecycle from discovery through to release.
  - Responsibilities: run discovery (`@explore`), present structured plans for user approval, delegate production code tasks to `@builder`, and coordinate `@test-writer` and `@reviewer` loops. Enforces approval gates and no auto-commits.

- **`agents/builder.md`** — Implementation Subagent
  - Role: Write production (runtime) code based on the approved plan.
  - Responsibilities: load architectural and framework-specific skills, read code before writing, implement features respecting interfaces and layer responsibilities, apply generic frontend quality rules when relevant, run lint/build checks, and never write tests. Reports with `IMPLEMENTATION COMPLETE.` or `BLOCKED.`

- **`agents/test-writer.md`** — Test Writer Subagent
  - Role: Write unit and integration tests for code produced by the builder.
  - Responsibilities: read implementation, mock external dependencies, write unit tests for exported behavior, write integration tests when applicable (external infra managed externally), verify tests pass, and never modify production code. Reports `TESTS PASSED.` or `TESTS BLOCKED.`

- **`agents/reviewer.md`** — Senior Code Reviewer
  - Role: Perform detailed code review focused on reliability and architecture.
  - Responsibilities: check for edge cases, error handling, and Clean Architecture violations; use architectural skills to validate design; return `REVIEW PASSED.` or a targeted list of issues.

## Skills

- **`skills/architectural-guidelines/SKILL.md`** — Clean Architecture Guidance
  - Purpose: Define layer responsibilities, entity invariants, service orchestration rules, repository patterns, and onboarding checks agents should run before coding.

- **`skills/go-architectural-guidelines/SKILL.md`** — Go-specific Architecture Rules
  - Purpose: Go directory conventions, dependency injection practices, error handling and verification steps for Go projects.

- **`skills/go-testing-guidelines/SKILL.md`** — Go-specific Testing Conventions
  - Purpose: Mock library preferences, test file conventions, integration test isolation, naming conventions, and verification commands for Go projects.

- **`skills/nextjs-frontend-guidelines/SKILL.md`** — Next.js Frontend Guidance
  - Purpose: Define Next.js-specific routing, server/client boundaries, data-fetching patterns, frontend quality rules, and verification expectations for Next.js projects.

- **`skills/commits/SKILL.md`** — Commit Message Formatting
  - Purpose: Provide agents with rules to format commit messages and require user confirmation for issue codes before committing.

## Notes

- Delegation rule: production code is always written by `@builder`; test code is always written by `@test-writer` (this is enforced in `agents/architect.md`).
- Agents should consult the architectural, language-specific, and framework-specific skills before making design or implementation decisions.
