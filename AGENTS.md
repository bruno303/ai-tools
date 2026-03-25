# AGENTS Guide

## Purpose
- This repository stores reusable agent prompts, reusable skills, and two small Bash helpers.
- Most files are Markdown with YAML frontmatter; the only executable files are `install.sh` and `ai-tools.sh`.
- Use this document as the first-stop operating guide for agentic coding agents working in this repo.

## Repository Layout
- `agents/` contains agent prompts such as `architect`, `builder`, `test-writer`, and `reviewer`.
- `skills/` contains reusable guidance modules, each in `skills/<skill-name>/SKILL.md`.
- `install.sh` copies `agents/` and `skills/` into another repository.
- `ai-tools.sh` provides a Docker wrapper function for running `opencode` against the current working tree.
- `README.md` is the high-level repository overview and inventory.

## External Rule Files
- No `.cursor/rules/` directory is present.
- No `.cursorrules` file is present.
- No `.github/copilot-instructions.md` file is present.
- If any of those files are added later, treat them as higher-priority instructions than this document and fold their guidance into future updates.

## Source of Truth
- Start with `README.md` for repo purpose and component inventory.
- Use `agents/architect.md` for orchestration flow and approval rules.
- Use `agents/builder.md` for implementation behavior and handback format.
- Use `agents/test-writer.md` for testing-agent scope and handback format.
- Use `agents/reviewer.md` for review criteria and severity rules.
- Use `skills/` files for architecture, Go, Next.js, and commit-style specifics.

## Build, Lint, and Test Reality
- There is no `Makefile`, `package.json`, `go.mod`, Python project file, or other repo-wide build system checked in.
- There is no configured linter for Markdown, Bash, or YAML in this repository.
- There is no formal automated test suite in this repository.
- Validation is therefore script-focused and manual-review-heavy; do not invent nonexistent commands.

## Practical Validation Commands
- Syntax-check the installer: `bash -n install.sh`
- Syntax-check the Docker helper: `bash -n ai-tools.sh`
- Verify installer usage text: `bash install.sh --help`
- Smoke-test installer into a temp directory: `tmpdir="$(mktemp -d)" && bash install.sh "$tmpdir"`
- Review local changes before handoff: `git diff -- AGENTS.md README.md agents/ skills/ install.sh ai-tools.sh`
- Check worktree status before handoff: `git status --short`

## Single-Target Checks
- Single-script validation: `bash -n install.sh`
- Other single-script validation: `bash -n ai-tools.sh`
- Single-command behavior check for installer help: `bash install.sh --help`
- There is no true single-test runner because no automated test harness exists.
- Single Markdown file verification is manual: read the file plus 1-2 similar files and confirm tone, frontmatter, and section structure match local conventions.

## Working Norms for Agents
- Read existing files before editing; this repo is mostly instructions and conventions.
- Keep diffs tight and scoped to the requested agent, skill, script, or docs.
- Preserve the repository's concise, directive tone.
- Avoid introducing tooling assumptions that are not already present.
- Do not claim a build, lint, or test command exists unless it is actually available from the repo root.
- Prefer updating existing guidance over creating duplicate guidance in multiple files.

## File Format Conventions
- Agent files are Markdown documents with YAML frontmatter.
- Skill files live at `skills/<skill-name>/SKILL.md` and also use YAML frontmatter.
- Preserve opening and closing `---` frontmatter delimiters exactly.
- Preserve existing frontmatter key names and ordering unless there is a strong reason to change them.
- Keep Markdown raw-source friendly: short sections, short bullets, low-noise phrasing.
- Prefer ASCII unless a file already requires non-ASCII content.

## Markdown Writing Style
- Use explicit headings and short bullet lists instead of dense paragraphs.
- Write in imperative, operator-facing language.
- Use backticks for paths, commands, identifiers, and literal phrases.
- Avoid decorative prose, motivational filler, and vague recommendations.
- Match the tone already used in `agents/*.md` and `skills/*/SKILL.md`.
- When documenting handback schemas, keep field names exact and easy to scan.

## Naming Conventions
- Agent filenames use lowercase kebab-case, for example `test-writer.md`.
- Skill directories use lowercase kebab-case, for example `go-testing-guidelines`.
- Skill content filename is always exactly `SKILL.md`.
- Keep new skill and agent names descriptive and narrowly scoped by role or technology.
- In prose, reuse the same term for the same concept across files; do not alternate between synonyms casually.
- For examples and placeholders, prefer short, explicit identifiers like `TASK_ID`, `DONE_WHEN`, and `BLOCKERS`.

## Imports and Dependencies Guidance
- This repository has almost no source-code import graph to manage because it is primarily Markdown plus Bash.
- For Markdown guidance files, prefer links and path references over duplicating long rule blocks across files.
- When editing agent prompts, reference shared skills by exact skill name rather than restating their full contents.
- Do not introduce references to external frameworks or libraries unless the repository is intentionally documenting them.
- If you add technology-specific rules, place them in the relevant skill instead of bloating generic agent prompts.

## Shell Script Style
- Follow the safer, clearer Bash style already demonstrated in `install.sh`.
- Use `#!/usr/bin/env bash` for new Bash scripts unless you are preserving an existing file-local convention.
- Use `set -euo pipefail` for non-trivial scripts.
- Quote variable expansions unless unquoted behavior is intentionally required.
- Prefer descriptive variable names like `clean_install`, `target_arg`, and `target_dir` over single-letter names.
- Use small helper functions for repeated output or option handling.
- Use `case` for flag parsing when options are simple.
- Keep filesystem operations explicit and safe; prefer `mkdir -p`, `cp -r --`, and guarded `rm -rf --` patterns.

## Types and Data Shape Guidance
- In Markdown schemas, keep field names stable once introduced.
- Prefer explicit enumerated statuses such as `STATUS: OK | BLOCKED` over free-form wording.
- Keep list item structures consistent within a section, especially for handback protocols.
- When adding YAML frontmatter keys, keep values simple scalars or small maps that match the existing style.
- Do not silently change a documented contract shape without updating every file that depends on it.

## Error Handling
- In Bash, fail fast on invalid input and return non-zero exit codes.
- Print user-facing error messages to stderr when appropriate.
- Handle expected failures explicitly; do not rely on silent fallthrough.
- In agent instructions, prefer explicit blocker reporting over guessing.
- Preserve exact handback phrases and status enums already used by the repo, such as `IMPLEMENTATION COMPLETE.`, `BLOCKED.`, `STATUS: OK`, or `STATUS: TESTS BLOCKED`, when editing the files that own those contracts.
- For Go guidance added to skills, prefer wrapped errors with `%w` and branching via `errors.Is` or `errors.As`.

## Architecture and Boundary Rules
- Respect `skills/architectural-guidelines/SKILL.md` as the generic architecture source of truth.
- Keep business rules out of delivery, framework, and infrastructure guidance unless the rule is explicitly about those boundaries.
- Put entity invariants on entities or value objects; put orchestration in services or use cases.
- Keep repository and gateway dependencies abstract at the business boundary.
- Avoid duplicating architecture rules across `AGENTS.md`, agent prompts, and skills unless the duplication materially improves execution quality.

## Repo-Specific Content Rules
- `agents/*.md` should describe role, scope, execution rules, and exact handback format.
- `skills/*/SKILL.md` should hold reusable domain, language, or framework rules rather than task-specific instructions.
- `README.md` should stay high-level and descriptive, not become the full rulebook.
- `AGENTS.md` should remain the operator manual for coding agents in this repo.
- If you add a new agent or skill, update `README.md` when the inventory has changed.

## Editing Guidance
- Prefer minimal diffs that preserve surrounding structure and wording.
- Keep established section order unless reordering clearly improves usability.
- Read 2-3 similar files before introducing new headings or schema shapes.
- Avoid formatting-only churn in Markdown files.
- Add comments to Bash only when they clarify non-obvious behavior.
- Do not rewrite unrelated prompt text while touching a nearby section.

## Consistency Checklist
- Does the file still read like an operator manual for agents?
- Are all file paths, skill names, and agent names exact?
- Are all documented commands real and runnable from the repo root?
- Did you avoid inventing a test harness, linter, or build pipeline?
- Are frontmatter keys preserved and still valid YAML?
- Are status labels and handback field names consistent with their owning files?
- Did you avoid claiming Cursor or Copilot rule files exist when they do not?

## When Adding New Tooling
- Add exact build, lint, and test commands here immediately.
- Add at least one narrow or single-target verification command when the tool supports it.
- Prefer commands that work from the repo root without extra wrappers.
- Document required environment variables or setup steps explicitly.
- If a new test harness is introduced, update the Single-Target Checks section with the narrowest useful test command.

## Handoff Expectations
- Summarize changed files clearly.
- Mention validation performed, even if it was only `bash -n` or manual review.
- Be honest about missing automation.
- Suggest the next useful follow-up only when grounded in the current repo state.
