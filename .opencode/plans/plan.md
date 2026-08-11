# Plan: Create an agent to write documentation of the software (Issue #3)

## Goal

Add a new reusable **documentation agent** ("documenter") to this repository, following the exact same structure and conventions as the existing agents (`builder`, `reviewer`, `spec-driver`). The agent is a subagent that reads the codebase and produces/updates accurate software documentation.

## Repository Context (must read before implementing)

- This repo ships reusable agent/skill definitions, not an application. There is **no build/lint/test framework**.
- **Canonical source of truth**: `opencode/agents/*.md` — Markdown prompt files with YAML frontmatter.
- **Generated mirror**: `codex/agents/*.toml` is generated from the markdown by `scripts/generate-codex-agents.sh` (run it after editing markdown; it reads frontmatter `description` and `permission.edit`, and maps `edit: deny` → `sandbox_mode = "read-only"`, else `"workspace-write"`). The prompt body **must not contain `"""`**.
- **Inventory**: `README.md` must be updated whenever an agent is added or removed (per `opencode/AGENTS.md` "Repo Reality").
- `opencode/install.sh` copies every `agents/*.md` into a target repo; codex TOMLs are installed by codex tooling, not by `install.sh`.
- Existing subagent prompts (`builder.md`, `reviewer.md`, `spec-driver.md`) share a consistent shape: frontmatter → `# Role` → `## Accepted Input` (structured block) → `## Execution Rules` → `## Completion Checklist` → `## Handback Protocol` (structured `STATUS: ...` output contract).

## Prior Art / Reference

The remote branch `ai/issue-3` (commit `7e468ec`, "feat: Create agent to write documentation of the software") already contains a draft implementation of exactly this issue. It can be used as a strong reference, but the plan below re-derives the content so the implementer does not depend on fetching that branch:

- `7e468ec:opencode/agents/documenter.md`
- `7e468ec:codex/agents/documenter.toml`
- README diff in `7e468ec`

If the implementer can access it (`git show 7e468ec:<path>`), it is a useful sanity check for tone and structure. Do not blindly copy it — the plan below is the spec.

## Confirmed Requirements

1. Create a new agent named `documenter` that writes and maintains accurate software documentation from the codebase.
2. Provide both runtime definitions: `opencode/agents/documenter.md` and the generated `codex/agents/documenter.toml`.
3. Update `README.md` inventory (overview line + Agents list + Operating Model).
4. The agent must be a **subagent** (`mode: subagent`) with `read`, `edit`, and `bash` permissions allowed (it needs to read code and write docs).
5. It must NOT invent behavior — documentation must be grounded in repository evidence; discrepancies between code and docs are flagged, not silently "fixed".
6. It must use a structured handback protocol (`STATUS: OK | BLOCKED`), consistent with `builder.md`.

## Open Questions (defaults chosen; confirm with user if they disagree)

- **Q1 — Naming**: `documenter` is chosen to match the existing branch name/prior art. Alternative: `doc-writer`, `docs-agent`. Default: `documenter`.
- **Q2 — Orchestrator integration**: Should `architect.md` be updated to delegate documentation tasks to `@documenter`? The issue only asks to "create an agent". Default: **no** changes to `architect.md` in this issue (keep scope minimal); note as a follow-up. If the user wants the architect to route doc work, add a task to update `opencode/agents/architect.md` + regenerate `codex/agents/architect.toml`.
- **Q3 — Scope of "documentation"**: README, architecture docs, API docs, module docs. The agent accepts `DOC_TARGETS` with these values as hints. Default: make the agent generic over doc targets, not specialized.
- **Q4 — New skill?**: Should a `skills/write-docs/SKILL.md` also be created? The issue says "agent", so default: **no new skill**; keep the change to agent definitions + README.

## Implementation Tasks

---

### Task 1: Create `opencode/agents/documenter.md`

**Files:**
- `opencode/agents/documenter.md` (new)

**Dependencies:** none

Create the canonical OpenCode agent prompt. Model it on `opencode/agents/builder.md` (structure, tone, permission block) and `opencode/agents/spec-driver.md` (evidence-grounded, no-assumption rules).

Frontmatter (required fields):

```yaml
---
description: Specialist in writing and maintaining accurate software documentation from the codebase.
mode: subagent
permission:
  read: allow
  edit: allow
  bash: allow
---
```

Body sections (follow the exact heading style of `builder.md`):

1. `# Role: Documentation Subagent` — specialist that produces/updates documentation reflecting the actual state of the codebase; does not write production code.
2. `## Accepted Input` — structured block with fields:
   - `DOC_TARGETS` (optional): `README`, `architecture`, `API`, `module`
   - `SCOPE` (optional)
   - `FILES` (optional): files to read/document
   - `DONE_WHEN` (required)
   - Note: missing optional sections tolerated if intent is clear (same tolerance as builder).
3. `## Execution Rules`:
   - Read before writing; base everything on repository evidence; do not invent features/behaviors/contracts.
   - Follow existing doc style/conventions; minimal edits; no unrelated refactors.
   - Protect contracts: when documenting public APIs/interfaces, record actual wire formats/schemas; flag doc↔code discrepancies rather than silently changing either.
   - Verification: cross-check documented commands/examples/claims against the codebase; run project-documented validation commands when relevant.
   - Stop on blockers (`STATUS: BLOCKED`) when the task is ambiguous or the codebase cannot support the requested documentation.
4. `## Completion Checklist` — every `DONE_WHEN` addressed; docs accurate against current codebase; no unrelated files changed; verification attempted and reported.
5. `## Handback Protocol` — exact structure:
   ```
   STATUS: OK | BLOCKED

   TASK_ID: ...
   FILES_MODIFIED: ...
   DOCUMENTATION_SUMMARY: ...
   VERIFICATION:
   - command: ...
     result: passed | failed | not_run
     notes: ...
   RISKS: ...
   BLOCKERS: ...
   ```
   With response rules: `STATUS: OK` only when complete & accurate; always include `TASK_ID`; list every created/modified file; keep summary focused; record every verification attempt; put follow-ups under `RISKS`; `BLOCKERS: - none` when none.

Constraints:
- Body must NOT contain a literal `"""` (breaks the codex generator).
- No `model:` line needed (builder.md has one, but it is optional; the codex generator ignores it and `install.sh` offers `--remove-model`).

---

### Task 2: Generate `codex/agents/documenter.toml`

**Files:**
- `codex/agents/documenter.toml` (new, generated)

**Dependencies:** Task 1

Run from repo root:

```bash
scripts/generate-codex-agents.sh
```

This regenerates all codex TOMLs from `opencode/agents/*.md`. It will create `codex/agents/documenter.toml` with:
- `name = "documenter"`
- `description = "Specialist in writing and maintaining accurate software documentation from the codebase."`
- `sandbox_mode = "workspace-write"` (because `permission.edit: allow`)
- `developer_instructions = """<markdown body>"""`

Verify:
- `git status --short` shows only the new `codex/agents/documenter.toml` (plus the Task 1 file and Task 3 README changes) — no unrelated TOMLs should change.
- `scripts/generate-codex-agents.sh --check` exits 0.
- The generated TOML body exactly matches the markdown body from Task 1 (minus frontmatter).

---

### Task 3: Update `README.md` inventory

**Files:**
- `README.md`

**Dependencies:** Task 1 (naming/content finalized)

Make three targeted edits, matching the existing concise tone:

1. Repository Overview list (line ~7): add `documenter` to the OpenCode agents list:
   `- \`opencode/agents/\` contains OpenCode agent prompts (\`architect\`, \`builder\`, \`spec-driver\`, \`reviewer\`, \`documenter\`) in Markdown.`
2. Agents section: change "The same four agents are defined for both runtimes:" → "The same five agents are defined for both runtimes:" and add a bullet after `spec-driver`:
   ```
   - **`documenter`** (`opencode/agents/documenter.md`, `codex/agents/documenter.toml`)
     - Specialist in writing and maintaining accurate software documentation from the codebase.
     - Documents only what the code actually does and can return `STATUS: OK` or `BLOCKED`.
   ```
3. Operating Model section (bottom): add one line, e.g.:
   `- \`documenter\` owns documentation and keeps it accurate against the codebase.`

Do not renumber or reorder other sections.

---

### Task 4 (optional, only if Q2 = yes): Wire `documenter` into `architect`

**Files:**
- `opencode/agents/architect.md`
- `codex/agents/architect.toml` (regenerate after editing the markdown)

**Dependencies:** Task 1, Task 2

If the user confirms the architect should route documentation work:
- Add `@documenter` to the `# Delegation` section of `architect.md` (e.g., "Documentation → `@documenter`").
- Optionally note in the review step that documentation-only tasks may skip `@reviewer`.
- Regenerate codex TOML: `scripts/generate-codex-agents.sh`.

If Q2 stays "no", skip this task entirely.

---

## Tests Required

There is no automated test framework in this repo. Verification consists of:

1. **Syntax check the generator** (unchanged, but cheap):
   `bash -n scripts/generate-codex-agents.sh`
2. **Codex TOML sync check** (the real test that markdown and TOML stay in sync):
   `scripts/generate-codex-agents.sh --check` → must exit 0 with no diff.
3. **Installer sanity** (opencode side):
   `bash -n opencode/install.sh` and `bash opencode/install.sh --help`
4. **Content checks** (manual, by implementer):
   - `grep -n '"""' opencode/agents/documenter.md` → no matches.
   - Frontmatter parses: `description` present, `mode: subagent`, `permission.edit: allow`.
   - `git diff` review: only `opencode/agents/documenter.md`, `codex/agents/documenter.toml`, `README.md` (+ optionally `architect.*`) changed.
5. **Smoke test (optional, recommended)**: install into a scratch dir and confirm the file lands:
   `mkdir -p /tmp/opencode/doc-smoke && opencode/install.sh /tmp/opencode/doc-smoke && ls /tmp/opencode/doc-smoke/agents/`

## Potential Risks

- **Codex drift**: Hand-editing the TOML or forgetting to run the generator leaves markdown and TOML out of sync; the `--check` gate catches this. Mitigation: always edit markdown, regenerate, run `--check`.
- **Generator failure**: A literal `"""` in the markdown body or missing `description` frontmatter makes `generate-codex-agents.sh` exit non-zero. Mitigation: Task 1 content check + Task 2 verification.
- **Scope creep**: Adding a companion skill or rewiring the architect expands the diff. Mitigation: keep to the three files unless the user answers Q2/Q4 affirmatively.
- **README staleness**: Forgetting to update `README.md` violates the repo's own rule ("If you add or remove an agent or skill, update README.md"). Mitigation: Task 3 is a hard dependency of "done".
- **Inconsistent handback schema**: If `documenter`'s output contract diverges from `builder`'s, orchestrators that parse structured output could mis-handle it. Mitigation: mirror builder's `STATUS: OK | BLOCKED` contract exactly (only the summary field name differs: `DOCUMENTATION_SUMMARY`).

## Rollout / Follow-ups

- No migrations, no runtime, no external dependencies.
- After merge, users get the agent automatically via `install.sh` (opencode) / the generated codex TOML.
- Follow-up candidates (out of scope unless requested): architect delegation (Q2), a `write-docs` skill (Q4), a docs-review pass by `@reviewer`.