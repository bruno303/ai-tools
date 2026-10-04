#!/usr/bin/env bash
#
# Idempotent OpenCode V2 sandbox environment.
#
# Sourced through BASH_ENV (/etc/sandbox-persistent.sh), /etc/profile.d and
# ~/.bashrc so interactive and non-interactive shells agree. It must not print
# to stdout on success: OpenCode and the sbx launch path consume shell output.
# shellcheck shell=bash

export GVM_ROOT="${GVM_ROOT:-$HOME/.gvm}"
export GO_VERSION="${GO_VERSION:-1.25.14}"

# gvm's command function. Sourcing scripts/env/gvm defines `gvm` (including
# `gvm use`) for agent subprocesses without loading gvm's interactive `cd`
# override, which is not nounset-safe. GVM_NO_GIT_BAK is exported so the
# function tolerates `set -u` shells (GVM_DEBUG must stay unset: a non-empty
# value makes the gvm launcher emit xtrace).
export GVM_NO_GIT_BAK="${GVM_NO_GIT_BAK:-}"
if [ -s "$GVM_ROOT/scripts/env/gvm" ]; then
  # shellcheck disable=SC1091
  . "$GVM_ROOT/scripts/env/gvm"
fi

# Deterministic fallback if gvm has no default environment yet, and a guard so
# `go` is always reachable.
export GOROOT="${GOROOT:-$GVM_ROOT/gos/go${GO_VERSION}}"
export GOPATH="${GOPATH:-$GVM_ROOT/pkgsets/go${GO_VERSION}/global}"

# Never let the Go command download a different toolchain at run time.
export GOTOOLCHAIN="${GOTOOLCHAIN:-local}"

for dir in "/home/agent/.local/bin" "$GVM_ROOT/bin" "$GOROOT/bin"; do
  case ":$PATH:" in
    *":$dir:"*) ;;
    *) export PATH="$dir:$PATH" ;;
  esac
done

# --- Proxy CA trust ---------------------------------------------------------
# sbx adds the proxy CA to the system bundle at sandbox start. Point every
# toolchain at the system bundle; TLS verification is never disabled.
export SSL_CERT_FILE="${SSL_CERT_FILE:-/etc/ssl/certs/ca-certificates.crt}"
export SSL_CERT_DIR="${SSL_CERT_DIR:-/etc/ssl/certs}"
export CURL_CA_BUNDLE="${CURL_CA_BUNDLE:-/etc/ssl/certs/ca-certificates.crt}"
export REQUESTS_CA_BUNDLE="${REQUESTS_CA_BUNDLE:-/etc/ssl/certs/ca-certificates.crt}"
export PIP_CERT="${PIP_CERT:-/etc/ssl/certs/ca-certificates.crt}"
export NODE_EXTRA_CA_CERTS="${NODE_EXTRA_CA_CERTS:-/etc/ssl/certs/ca-certificates.crt}"
export GIT_SSL_CAINFO="${GIT_SSL_CAINFO:-/etc/ssl/certs/ca-certificates.crt}"
