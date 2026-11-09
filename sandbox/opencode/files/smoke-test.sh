#!/usr/bin/env bash
#
# Local toolchain smoke test for the OpenCode V2 sandbox image.
#
# Safe to run inside a sandbox and in the built image:
#   * uses only local resources under a temporary directory,
#   * makes no provider/model calls and no other network requests,
#   * never reads credentials or environment secrets,
#   * never writes to the mounted workspace.
#
# It verifies the workload architecture (OpenCode V2, Go 1.25.x through gvm),
# the basic tool set, an offline Go compile+test, Node/npm, a Python venv and
# uv/uvx. Runtime properties that need a real Windows/sbx host (credentials,
# OAuth, TUI, restart persistence, workspace mount, private daemon) are printed
# as a manual checklist; this script cannot prove them.
set -u

QUICK=0
for arg in "$@"; do
  [ "$arg" = "--quick" ] && QUICK=1
done

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/opencode-smoke.XXXXXX")"
trap 'rm -rf "$TMP_ROOT"' EXIT

FAILURES=0
pass() { printf 'PASS  %s\n' "$1"; }
fail() { printf 'FAIL  %s\n' "$1"; FAILURES=$((FAILURES + 1)); }
section() { [ "$QUICK" -eq 1 ] || printf '\n== %s ==\n' "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }
assert_cmd() { name="$1"; shift; if "$@" >/dev/null 2>&1; then pass "$name"; else fail "$name"; fi; }

section "Architecture and versions"
if [ "$(uname -m)" = "x86_64" ]; then
  pass "linux/amd64 workload"
else
  fail "expected x86_64 workload, got $(uname -m)"
fi

OPENCODE_VERSION_OUTPUT="$(opencode --version 2>/dev/null | head -n1 || true)"
case "$OPENCODE_VERSION_OUTPUT" in
  *v2.*|2.*) pass "OpenCode V2 ($OPENCODE_VERSION_OUTPUT)" ;;
  *) fail "OpenCode V2 not detected ('$OPENCODE_VERSION_OUTPUT')" ;;
esac
if have opencode2; then pass "opencode2 command present"; else fail "opencode2 command missing"; fi

GO_VERSION_OUTPUT="$(go version 2>/dev/null || true)"
case "$GO_VERSION_OUTPUT" in
  *"go1.25."*) pass "$GO_VERSION_OUTPUT" ;;
  *) fail "Go 1.25.x not detected ('$GO_VERSION_OUTPUT')" ;;
esac
case "$(go env GOROOT 2>/dev/null || true)" in
  */.gvm/gos/go1.25.*) pass "Go resolved from the gvm tree" ;;
  *) fail "Go GOROOT is not under gvm" ;;
esac
if have gvm; then pass "gvm command available"; else fail "gvm command missing"; fi

section "Agent launch and proxy CA trust"
assert_cmd "shell environment directory traversable" test -x /usr/local/share/opencode-kit
assert_cmd "shell environment file readable" test -r /usr/local/share/opencode-kit/shell-env.sh
assert_cmd "persistent shell environment readable" test -r /etc/sandbox-persistent.sh
assert_cmd "noninteractive Bash environment loads" bash -c '. /etc/sandbox-persistent.sh'
for shell in /bin/sh /bin/bash; do
  if [ -x "$shell" ]; then pass "$shell executable"; else fail "$shell missing or not executable"; fi
done
for var in SSL_CERT_FILE SSL_CERT_DIR CURL_CA_BUNDLE REQUESTS_CA_BUNDLE PIP_CERT NODE_EXTRA_CA_CERTS GIT_SSL_CAINFO; do
  value="$(eval "printf '%s' \"\${$var:-}\"")"
  if [ -n "$value" ]; then pass "$var is set"; else fail "$var is not set"; fi
done
if [ -f /etc/ssl/certs/ca-certificates.crt ]; then pass "system CA bundle present"; else fail "system CA bundle missing"; fi
if [ "${GIT_SSL_NO_VERIFY:-}" = "1" ] || [ "${NODE_TLS_REJECT_UNAUTHORIZED:-}" = "0" ]; then
  fail "TLS verification is disabled"
else
  pass "TLS verification not disabled"
fi

section "Basic tools"
for tool in bash sh git make gcc g++ pkg-config ssh curl wget jq rg fd fzf less tree tar gzip xz zip unzip python3 pip3 node npm uv uvx; do
  if have "$tool"; then pass "$tool"; else fail "$tool"; fi
done

section "Go compile and test (offline)"
mkdir -p "$TMP_ROOT/go"
cat > "$TMP_ROOT/go/go.mod" <<'EOF'
module sandbox.smoke/hello

go 1.25
EOF
cat > "$TMP_ROOT/go/hello.go" <<'EOF'
package hello

// Add returns the sum of a and b.
func Add(a, b int) int { return a + b }
EOF
cat > "$TMP_ROOT/go/hello_test.go" <<'EOF'
package hello

import "testing"

func TestAdd(t *testing.T) {
	if got := Add(2, 3); got != 5 {
		t.Fatalf("Add(2,3) = %d, want 5", got)
	}
}
EOF
if ( cd "$TMP_ROOT/go" && GOTOOLCHAIN=local GOFLAGS=-mod=mod go test ./... >/dev/null 2>&1 ); then
  pass "go build + test"
else
  fail "go build + test"
fi

section "Node and npm"
assert_cmd "node --version" node --version
assert_cmd "node evaluates JavaScript" node -e "process.exit(1 + 1 === 2 ? 0 : 1)"
NPM_VERSION_OUTPUT="$(npm --version 2>/dev/null || true)"
if [ -n "$NPM_VERSION_OUTPUT" ]; then pass "npm $NPM_VERSION_OUTPUT"; else fail "npm --version"; fi

section "Python and venv"
assert_cmd "python3 --version" python3 --version
if python3 -m venv "$TMP_ROOT/venv" >/dev/null 2>&1 \
  && "$TMP_ROOT/venv/bin/python" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' >/dev/null 2>&1; then
  pass "python3 venv creation"
else
  fail "python3 venv creation"
fi

section "uv and uvx"
assert_cmd "uv --version" uv --version
assert_cmd "uvx --version" uvx --version

section "Manual runtime checklist (not automatable here)"
cat <<'EOF'
MANUAL  On a Windows PowerShell host with sbx 0.46.0:
MANUAL  1. Run the kit, e.g.:
MANUAL     sbx run --name opencode-dev "C:\path with spaces\sandbox\opencode"
MANUAL  2. Approve the OpenCode Go credential binding when prompted.
MANUAL  3. In the TUI run /connect and finish ChatGPT Pro/Plus (headless) OAuth.
MANUAL  4. Confirm the TUI starts, a model responds, and a trivial edit lands.
MANUAL  5. Restart the sandbox and confirm ChatGPT auth and sessions persist.
MANUAL  6. Confirm the workspace mount is visible and the sandbox has its own
MANUAL     Docker daemon and does not mount the host Docker socket.
MANUAL  7. Delete the sandbox and confirm auth/session state is lost.
EOF

printf '\nsmoke-test: %d failure(s)\n' "$FAILURES"
[ "$FAILURES" -eq 0 ]
