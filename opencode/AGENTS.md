# AGENTS Guide

## Purpose
- This repo ships reusable OpenCode agents and skills, not an application runtime.
- `install.sh` installs only `agents/` and `skills/` into another repository.

## Start Here
- Read `README.md` first for the inventory and intended role of each agent and skill.
- Read the specific prompt or skill you are editing before changing it; behavior contracts live in those files.
- `opencode.jsonc` enables a local Serena MCP server via `uvx`; several prompts require Serena-first repository inspection when available.

## Structure That Matters
- `agents/*.md` are model-only Markdown profiles with YAML frontmatter. The active set is `executor.md` and `reviewer.md`; retired definitions are under `../archive/opencode/agents/` and are not installed.
- `skills/<skill-name>/SKILL.md` are Markdown skill files with YAML frontmatter.
- `plugins/wsl-notify.ts` exists for local OpenCode usage, but it is not installed by `install.sh`.
- `install.sh` does not copy `AGENTS.md`, `README.md`, `plugins/`, or `opencode.jsonc`.

## Model Profile Contract
- Keep active agent files limited to harness metadata and model selection.
- Do not add behavioral prompts, handback schemas, or workflow coordination to active agent files; those belong in skills.
- The former `architect`, `builder`, `spec-driver`, and prior reviewer prompts are archived under `../archive/opencode/agents/`; they are not active installation inputs.

## Verified Commands
- Syntax check installer: `bash -n install.sh`
- Syntax check Docker helper: `bash -n ai-tools.sh`
- Verify installer usage: `bash install.sh --help`

## Script Behavior Worth Remembering
- `install.sh` accepts `--clean` or `-c`, a positional target directory, or `TARGET_DIR`, and preserves `--remove-model` for compatibility.
- `install.sh` delegates active OpenCode agent installation to `../install-agents.sh`, which replaces only `agents/executor.md` and `agents/reviewer.md`.
- The root installer also supports Codex (`<target>/.codex/agents`) and Claude (`<target>/.claude/agents`).
- `ai-tools.sh` defines `opencode-run()` as a Docker wrapper that mounts the current working tree plus OpenCode config and state directories.

## Repo Reality
- There is no repo-wide build, lint, or automated test config checked in. Do not invent commands that are not present.
- If you add or remove an agent or skill, update `README.md` because it is the inventory users will read first.
- Match the existing concise, operator-facing tone; keep diffs tight and avoid duplicating guidance that already lives in a skill.
