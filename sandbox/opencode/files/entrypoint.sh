#!/usr/bin/env bash
#
# OpenCode V2 workload entrypoint.
#
# An sbx@1 host reads this image's ENTRYPOINT and launches it itself (under
# bash, with BASH_ENV sourced); the entrypoint must never become PID 1 of the
# image. This script performs the small, synchronous per-sandbox setup that
# must finish before the agent starts, then execs OpenCode so signals and the
# exit code pass through unchanged.
set -euo pipefail

export HOME="${HOME:-/home/agent}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
export XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"

# A sandbox can start with a fresh home overlay and an empty workspace mount.
# Make sure OpenCode's state directories exist before the server opens its
# SQLite database (auth tokens and sessions live there).
mkdir -p \
  "$XDG_DATA_HOME/opencode" \
  "$XDG_CONFIG_HOME/opencode" \
  "$XDG_STATE_HOME/opencode" \
  "$XDG_CACHE_HOME/opencode"

# Load the persistent environment (Go via gvm, proxy CA trust, and any exports
# the user appended to /etc/sandbox-persistent.sh).
if [ -s /etc/sandbox-persistent.sh ]; then
  # shellcheck disable=SC1091
  . /etc/sandbox-persistent.sh
fi

# Default launch: a private, standalone OpenCode V2 TUI/server for this
# sandbox. "$@" forwards arguments supplied through sbx unchanged.
if [ "$#" -eq 0 ]; then
  exec opencode --standalone
fi

# OpenCode V2 accepts --standalone only on commands that own a server (the
# default TUI command and `run`); it rejects the flag on others such as
# `debug`, and when it trails them. Forward explicit arguments verbatim so
# every subcommand and its flags work; callers that need a private server pass
# --standalone on the commands that support it.
exec opencode "$@"
