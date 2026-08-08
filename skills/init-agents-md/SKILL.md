---
name: init-agents-md
description: Use when setting up, creating, generating, or updating the root AGENTS.md file for a repository (triggers on "init agents md", "set up AGENTS.md", "create AGENTS.md", "update AGENTS.md", "generate agents file"). Produces an evidence-based operational guide for development agents covering workflows, commands, architecture, conventions, observability, infra, testing, and working rules.
---

# When to use
Use for:
- a repository that has no AGENTS.md yet (setup)
- an existing AGENTS.md that is outdated, wrong, or lacks operational guidance

Do not use for:
- editing the current repository's own AGENTS.md conventions
- documentation that is not the root AGENTS.md

# Goal
Create or update the root AGENTS.md as a high-signal operational guide for development agents. Base everything on repository evidence: source code, manifests, config, Docker/Compose, CI, docs, migrations, and tests. Do not invent missing details. Preserve useful existing AGENTS.md content, but rewrite for clarity and completeness. Optimize the final file for agent execution quality, not human marketing text.

# Process
1. Discover the stack from manifests (package.json, go.mod, pyproject.toml, Cargo.toml, etc.) and package manager lockfiles.
2. Discover commands from Makefile, package.json scripts, docker-compose.yml, justfile, Taskfile, CI workflows (.github/workflows, .gitlab-ci.yml), and scripts/.
3. Map the top-level directory structure and trace dependency direction between the most important directories.
4. Find evidence for conventions (formatter/linter configs), observability, infra resources, and testing setup.
5. Read the existing AGENTS.md (if any) and keep content that is still accurate.
6. If all of test/build/start-infra commands are undiscoverable from evidence, stop and ask the user before writing.
7. Write the file to the repository root as `AGENTS.md`.

# Rules
- Never invent commands, workflows, or architecture; only state what evidence shows.
- Mark anything unclear as `Unknown` or `Needs confirmation` in the file.
- Target roughly 100-150 lines; use tables and one-line bullets, not prose.
- Do not enumerate generated/build/vendor directories beyond one line saying to ignore them.
- Prefer the exact invocation from evidence; do not normalize or guess flags.
- If a command appears only in docs and not in executable config, add `(Needs confirmation)`.

# Output
Write `AGENTS.md` with the following sections, in this order (most operationally relevant first):

1. **Project Overview** — 2-4 sentences: what the project is, primary interface (CLI/service/library), entry points.
2. **Stack Summary** — languages, frameworks, package manager, key versions from manifests.
3. **High-Level Workflows** — the most important operational loops, each as goal -> exact ordered commands: install dependencies, run the app, build, start local infrastructure, run a single test, run the full suite, verify a change before handback, deploy (if present in repo). Fastest loop first.
4. **Development Commands** — a table: Category | Command (exact, from evidence) | Working dir | What it does | Notes. Cover at minimum: build, test (full + targeted), lint/format, start app, start infra (`docker compose up -d` and equivalent), migrate DB, generate code.
5. **Architecture** — the top ~5-10 most important directories, each with: one-line role, key files inside, relationship to other directories (who depends on it, what it produces). Then 2-4 lines on dependency direction and data/control flow, plus a "reading order" line recommending which directories to read first.
6. **Code Conventions** — evidence-based rules only: formatting, naming, error handling, package/module layout, config style; include only what code or tooling actually enforces.
7. **Observability** — where logs, metrics, traces, and alerts live and how to view them (commands, dashboards, datasources, log queries). `N/A` if no evidence.
8. **Infrastructure and External Resources** — Docker/Compose services, databases, message brokers, external APIs, secrets/env files, ports, startup order.
9. **Testing Strategy** — test levels present, framework and runner commands, how to run a single test, what CI runs, coverage gates.
10. **Agent Working Rules** — search before reading broadly; read only relevant sections; ignore generated/vendor directories; verify changes with the fastest relevant workflow before handback; keep diffs minimal; update README/docs when structure changes.
11. **Known Gaps or Unknowns** — an explicit list of everything marked Unknown or Needs confirmation, so the next agent knows what to verify.
