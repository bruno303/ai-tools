# OpenCode V2 sandbox

This sandbox runs OpenCode V2 (`opencode --standalone`) as the non-root
`agent` user (UID 1000). It is an isolated sandbox with its own daemon and
filesystem; it does not mount the host Docker socket.

## Toolchain

- Go 1.25.x, installed through `gvm` (the `gvm` command works in
  non-interactive shells; `GOTOOLCHAIN=local` prevents toolchain downloads).
- Node.js LTS with npm.
- Python 3 with `venv`, plus `uv` and `uvx`.
- Git, Make, GCC/G++, pkg-config, OpenSSH, curl, wget, jq, ripgrep (`rg`),
  `fd`, `fzf`, `less`, `tree` and common archive tools.

Run `smoke-test.sh` for a local check of this toolchain. It makes no network
calls and does not touch the workspace.

## Project guidance precedence

Follow the project's own `AGENTS.md`, `README`, and contributing instructions
first. This file is sandbox guidance only and must not override project
guidance. If they conflict, prefer the project.

## Environment

- `/etc/sandbox-persistent.sh` is the persistent shell environment and is
  loaded through `BASH_ENV`. Add exports that later commands need there.
- Non-interactive Bash sources that file, so keep it free of interactive-only
  commands and keep it quiet (no output).
- The system CA bundle at `/etc/ssl/certs/ca-certificates.crt` is the trust
  anchor; TLS verification is never disabled.

## Limits of this environment

Network egress is proxy-enforced and allow-listed by the kit, and declared
service credentials are injected by the host proxy rather than stored in the
sandbox. That is containment for the listed services; it is not a claim that
the agent, the workspace, or arbitrary code is trusted. Review changes before
applying them on the host.
