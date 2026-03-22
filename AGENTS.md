# AGENTS Guide

## Purpose
- This repository stores agent definitions, reusable skills, and a helper install script.
- Most source files are Markdown with YAML frontmatter; the only executable code in-repo is `install.sh`.
- Use this file as the first-stop operating guide for agentic coding agents working here.

## Repository Layout
- `agents/` contains agent prompts such as `architect`, `builder`, `test-writer`, and `reviewer`.
- `skills/` contains named skills, each in its own directory with a `SKILL.md` file.
- `install.sh` installs `agents/` and `skills/` into another target repository.
- `README.md` documents the role of each agent and skill at a high level.

## External Rule Files
- No `.cursor/rules/` directory is present.
- No `.cursorrules` file is present.
- No `.github/copilot-instructions.md` file is present.
- If any of those files are added later, treat them as higher-priority repository instructions and update this document.

## Source of Truth
- For repo purpose and component inventory, start with `README.md`.
- For orchestration behavior, use `agents/architect.md`.
- For implementation behavior, use `agents/builder.md`.
- For test expectations, use `agents/test-writer.md`.
- For review expectations, use `agents/reviewer.md`.
- For architecture and language/framework rules, use the files under `skills/`.

## Build, Lint, and Test Commands
- There is no `Makefile`, `package.json`, `go.mod`, or other project-wide build system in this repository.
- There are no dedicated repo-level lint scripts checked in.
- There are no dedicated repo-level automated test commands checked in.
- There is no existing single-test runner because the repository does not contain a formal test suite.

## Practical Validation Commands
- For shell syntax validation of the only script: `bash -n install.sh`
- For usage verification of the helper script: `bash install.sh --help`
- For reviewing local modifications: `git diff -- AGENTS.md agents/ skills/ install.sh README.md`
- For repository status before handoff: `git status --short`

## Single-File or Single-Target Checks
- Single shell script validation: `bash -n install.sh`
- Single Markdown file review is manual; there is no markdown linter configured.
- Single skill/agent verification is manual: read the target file plus any referenced companion files.
- If you add a new test harness in the future, update this section with exact single-test commands.

## Working Norms for Agents
- Read existing files before editing; this repo is mostly prompt engineering and convention management.
- Preserve the repository's concise, instruction-heavy writing style.
- Keep changes scoped: update only the agent, skill, or doc files relevant to the task.
- Avoid introducing tooling assumptions that are not already present in the repository.
- Do not invent commands, scripts, or project capabilities and present them as existing behavior.

## File Format Conventions
- Agent files are Markdown documents with YAML frontmatter at the top.
- Skills live in `skills/<skill-name>/SKILL.md` and also use YAML frontmatter.
- Keep frontmatter keys simple and stable; preserve existing key names when editing.
- Prefer plain ASCII unless a file already requires another character set.
- Keep line content easy to scan in raw Markdown.

## Frontmatter Rules
- Preserve the opening and closing `---` delimiters exactly.
- Do not reorder frontmatter keys unless there is a strong reason.
- Keep `description` short and role-oriented.
- Preserve `mode`, `temperature`, and `permission` fields where present.
- When adding permissions, follow the existing allowlist style and be specific.

## Markdown Style
- Use short sections with explicit headings.
- Prefer bullet lists over dense paragraphs.
- Keep wording directive, concrete, and imperative.
- Use backticks for paths, commands, identifiers, and literal phrases.
- Avoid decorative prose; optimize for agent readability.
- Match the tone already used in `agents/*.md` and `skills/*/SKILL.md`.

## Naming Conventions
- Agent filenames use lowercase kebab-case, e.g. `test-writer.md`.
- Skill directory names use lowercase kebab-case, e.g. `go-testing-guidelines`.
- Skill content file name is always exactly `SKILL.md`.
- Keep new skill names descriptive and scoped by concern or technology.
- In prose, use consistent terminology for the same concept across files.

## Imports and Dependencies
- There are no source-code import conventions to enforce across the repository because it is primarily Markdown plus one shell script.
- When writing guidance about code imports for downstream projects, keep it technology-specific and place it in the relevant skill.
- Do not add references to external libraries or frameworks unless the repository is intentionally documenting them.

## Shell Script Style
- Follow the style already used in `install.sh`.
- Use `#!/usr/bin/env bash` for Bash scripts.
- Keep `set -euo pipefail` at the top of non-trivial scripts.
- Quote variable expansions unless unquoted behavior is explicitly required.
- Prefer long, descriptive variable names such as `clean_install` and `target_arg`.
- Use small helper functions for repeated behavior like usage output.
- Use `case` for option parsing when flags are simple.
- Keep filesystem operations explicit and safe.

## Error Handling
- In shell, fail fast and return non-zero exit codes on invalid input.
- Print user-facing errors to stderr when appropriate.
- In agent instructions, prefer explicit blocker reporting over guessing.
- Preserve the repository pattern of returning exact handback phrases like `IMPLEMENTATION COMPLETE.` or `BLOCKED.`.
- For Go-specific guidance, follow `fmt.Errorf("operation: %w", err)` wrapping as documented in the Go skill.

## Architecture Guidance
- Respect the Clean Architecture rules in `skills/architectural-guidelines/SKILL.md`.
- Keep business logic out of infrastructure/framework layers in any guidance you add.
- Put entity invariants on entities and orchestration in services/use-cases.
- Keep repository and gateway dependencies abstract at the domain boundary.
- Do not duplicate architectural rules across files unless the duplication improves agent execution materially.

## Frontend and Next.js Guidance
- Generic frontend implementation rules live in `agents/builder.md`.
- Next.js-specific implementation rules live in `skills/nextjs-frontend-guidelines/SKILL.md`.
- If you update frontend guidance, keep the generic rules in the builder and framework-specific rules in the skill.
- Preserve the documented preference for responsive, accessible, low-complexity UI decisions.

## Testing Guidance
- This repository currently documents test strategy more than it runs tests itself.
- `agents/test-writer.md` defines how the testing subagent should behave.
- `skills/go-testing-guidelines/SKILL.md` is the source of truth for Go test naming, integration isolation, and verification commands.
- Do not add fake test instructions to `AGENTS.md`; only document commands that actually exist here.

## Editing Guidance
- Prefer minimal diffs that preserve surrounding wording and structure.
- When modifying an existing agent or skill, keep its established section order unless a reorganization clearly improves usability.
- If you add a new skill, also consider whether `README.md` should list it.
- If you add new repository-wide conventions, document them here.
- If you change agent handback phrases, update any dependent docs that mention them.

## Consistency Checklist
- Does the file still read like an operator manual for agents?
- Are file paths, skill names, and agent names exact?
- Are all documented commands actually available in this repo?
- Are instructions consistent with `README.md` and the relevant `agents/` or `skills/` files?
- Did you avoid claiming the existence of Cursor or Copilot rules when none are present?

## When Adding New Tooling
- Add the exact build, lint, and test commands here.
- Include at least one single-target command if the tool supports it.
- Prefer commands that work from the repo root.
- Note any required environment variables or setup steps.
- Keep commands copy-pasteable.

## Handoff Expectations
- Summarize changed files clearly.
- Mention any validation you performed, even if it was only `bash -n install.sh` or manual review.
- Call out missing automation honestly when relevant.
- Suggest the next most useful follow-up only when it is grounded in the current repo state.
