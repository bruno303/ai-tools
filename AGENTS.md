# AGENTS Guide

## Purpose
- This repo ships reusable OpenCode agents and skills, not an application runtime.
- `install.sh` installs only `agents/` and `skills/` into another repository.

## Start Here
- Read `README.md` first for the inventory and intended role of each agent and skill.
- Read the specific prompt or skill you are editing before changing it; behavior contracts live in those files.
- `opencode.jsonc` enables a local Serena MCP server via `uvx`; several prompts require Serena-first repository inspection when available.

## Structure That Matters
- `agents/*.md` are Markdown prompt files with YAML frontmatter.
- `skills/<skill-name>/SKILL.md` are Markdown skill files with YAML frontmatter.
- `plugins/wsl-notify.ts` exists for local OpenCode usage, but it is not installed by `install.sh`.
- `install.sh` does not copy `AGENTS.md`, `README.md`, `plugins/`, or `opencode.jsonc`.

## Prompt Contracts To Preserve
- Keep exact handback schemas and status labels stable unless you intentionally update the owning prompt everywhere it is relied on.
- Preserve role boundaries encoded in the prompts:
- `architect` delegates and requires explicit `Approve` before execution.
- `builder` does not write tests.
- `test-writer` does not change production code.
- `reviewer` is read-only.
- `freelancer` is the single-agent full-delivery path for small tasks.

## Verified Commands
- Syntax check installer: `bash -n install.sh`
- Syntax check Docker helper: `bash -n ai-tools.sh`
- Verify installer usage: `bash install.sh --help`

## Script Behavior Worth Remembering
- `install.sh` accepts `--clean` or `-c`, a positional target directory, or `TARGET_DIR`.
- `install.sh` replaces existing destination files and copies every `agents/*.md` file plus every directory under `skills/`.
- `ai-tools.sh` defines `opencode-run()` as a Docker wrapper that mounts the current working tree plus OpenCode config and state directories.

## Repo Reality
- There is no repo-wide build, lint, or automated test config checked in. Do not invent commands that are not present.
- If you add or remove an agent or skill, update `README.md` because it is the inventory users will read first.
- Match the existing concise, operator-facing tone; keep diffs tight and avoid duplicating guidance that already lives in a skill.
