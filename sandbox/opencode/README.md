# OpenCode V2 Docker Sandboxes kit

A native Docker Sandboxes (schema **v3**) workload kit that runs **OpenCode V2**
on Ubuntu 24.04 LTS for a linux/amd64 sandbox. It is independent of the built-in
`opencode` workload, which ships OpenCode V1.

The kit is one workload and no mixins. It installs its own toolchain at image
build time: Go 1.25.x through [gvm](https://github.com/moovweb/gvm), Node.js
LTS/npm, Python 3 + `venv` + `uv`/`uvx`, Git, Make, GCC/G++, pkg-config,
OpenSSH, curl/wget/jq, ripgrep, fd, fzf, less, tree and common archivers.
OpenCode launches with a private `--standalone` server and forwards arguments
through. Because the V2 CLI accepts `--standalone` only on commands that own a
server, the kit applies it to the default (no-argument) launch and forwards any
explicit arguments unchanged.

## Files

```text
sandbox/opencode/
├── opencode.yaml          # v3 workload descriptor
├── opencode.dockerfile    # companion image recipe
├── context.md             # agent-context body (staged as AGENTS.md)
├── .dockerignore
├── README.md
└── files/
    ├── entrypoint.sh      # no args: `opencode --standalone`; else args verbatim
    ├── shell-env.sh       # Go/gvm + proxy CA shell environment
    └── smoke-test.sh      # local toolchain smoke test
```

## Requirements

- Windows PowerShell host with **sbx 0.46.0**.
- Docker with Buildx for local builds and publication.
- A ChatGPT subscription (Plus/Pro) and/or an OpenCode Go subscription. Keys
  are never required by the kit itself.

## Build locally (descriptor build)

The descriptor's `# syntax=docker/sandbox-kit:3` line selects the Kit frontend;
the companion Dockerfile is found by the matching `opencode` stem.

```powershell
docker buildx build --platform linux/amd64 `
  -f .\sandbox\opencode\opencode.yaml `
  -t ai-tools-opencode-kit:dev --load .\sandbox\opencode
```

`sbx` can also build the directory directly when you create the sandbox, so a
separate build is optional.

## Run locally

Quote paths that contain spaces.

```powershell
# Local kit directory (space-safe quoting)
sbx run --name opencode-dev "C:\path with spaces\docker-sandbox-opencode\sandbox\opencode"

# Or from a published/loaded image reference
sbx run --name opencode-dev ai-tools-opencode-kit:dev
```

The first run on a third-party kit asks you to approve its credential request
(see [Authentication](#authentication)).

## Publish (example only, not performed here)

```powershell
docker buildx build .\sandbox\opencode `
  --file .\sandbox\opencode\opencode.yaml `
  --platform linux/amd64 `
  --tag docker.io/<NAMESPACE>/opencode-v2:2.0.22 `
  --push
```

To ship a different OpenCode V2 build, add
`--build-arg opencodeVersion=<version>`; kit argument names are declared in
`opencode.yaml`.

## Authentication

Two providers are wired, and nothing forces a model:

### ChatGPT subscription OAuth (recommended)

Inside the sandbox TUI run `/connect`, choose **OpenAI**, then
**ChatGPT Pro/Plus (headless)** and complete the flow. OpenCode V2 stores the
resulting OAuth tokens in its server SQLite database
(`~/.local/share/opencode/opencode.db`, printed by `opencode debug paths db`).

- Tokens stay in the sandbox; the kit does not import host credentials.
- A stopped/started sandbox keeps them; deleting the sandbox loses them.
- After connecting, use `/models` to pick a model.

### OpenCode Go (host-side binding)

The kit declares a proxy-managed credential named `opencode-go`. The real key
stays on the host:

```powershell
# Store the OpenCode Go key on the host (prompts for the value)
sbx secret set opencode-go
```

Approve the kit's credential binding when prompted (recorded in
`%APPDATA%\sbx\credentials.yaml`). The sandbox receives only a sentinel in
`OPENCODE_API_KEY`; the host proxy injects `Authorization: Bearer <key>` for
requests to `opencode.ai`. Then select an `opencode-go/<model>` model.

- Do **not** paste a real OpenCode Go key into `/connect` or any sandbox shell:
  that would store the real key inside the sandbox.
- If no binding is approved, the optional credential is withheld and ChatGPT
  OAuth still works.

Network egress is limited to the provider endpoints declared in
`opencode.yaml`. Add host policy for any additional hosts your projects need.

## Versions, upgrade, provenance

| Component | Pin | Provenance |
|---|---|---|
| OpenCode V2 | 2.0.22 | `@opencode/cli` npm package (registry integrity) |
| Go | 1.25.14 | go.dev official tarball SHA-256 `a21ae563…f7712` |
| gvm | commit `dd652539fa4b771840846f8319fad303c7d0a8d2` | moovweb/gvm checkout |
| Node.js LTS | 24.21.0 | nodejs.org tarball SHA-256 `6e1db87e…dc5ff` |
| uv/uvx | 0.12.23 | PyPI manylinux x86_64 wheel SHA-256 `565c6e28…b2fff` |
| Base | ubuntu:24.04 | Docker official image |

Upgrades are explicit: change the matching default in `opencode.yaml` (and,
when relevant, the checksum/build arg in `opencode.dockerfile`), then rebuild
and create a new sandbox. The kit sets `"update": "disable"` so a running
OpenCode never moves itself inside the sandbox.

## Sessions, restart and deletion

- Auth tokens and session state live in the sandbox SQLite database.
- Restarting the same sandbox (`sbx stop` / `sbx start`) preserves them.
- Deleting the sandbox (`sbx rm`) removes them permanently; you re-run
  `/connect` afterwards. Keep durable project state in the mounted workspace.

## Private keys

SSH agent forwarding is the default in Docker Sandboxes: the private key never
enters the sandbox, and processes there can only request signatures. Never copy
private keys, tokens, or API keys into the workspace or the sandbox filesystem.
The proxy-managed credential and OAuth sentinels keep declared secrets on the
host.

## Smoke test

Run inside the sandbox or in the built image:

```bash
smoke-test.sh
```

It checks the architecture (OpenCode V2, Go 1.25.x via gvm) and basic tools,
compiles and tests a tiny offline Go program, runs Node/npm, creates a Python
venv, and validates `uv`/`uvx`. It makes no provider calls, does not read
credentials, and does not modify the workspace. It also prints the manual
runtime checklist below.

## Manual runtime checklist (not verified in this repository)

This repository has no Windows host or `sbx`, so none of the following is
claimed as passed. Verify them on a real host:

- [ ] Create the sandbox on Windows PowerShell with `sbx 0.46.0`, including a
      kit path that contains spaces.
- [ ] Approve the OpenCode Go credential binding and confirm the sandbox only
      sees a sentinel in `OPENCODE_API_KEY`.
- [ ] Complete ChatGPT Pro/Plus (headless) OAuth with `/connect`.
- [ ] Confirm the TUI starts, a model responds, and a workspace edit lands.
- [ ] Restart the sandbox and confirm ChatGPT auth and sessions persist.
- [ ] Confirm the workspace mount is visible and the sandbox has its own Docker
      daemon (no host socket mount).
- [ ] Delete the sandbox and confirm auth/session state is gone.

## Notes

- linux/amd64 only; no ARM64, no web/desktop UI.
- One workload, no mixins, per the Docker sandbox kit model.
- No host Docker launcher or host Docker socket mount is used.
