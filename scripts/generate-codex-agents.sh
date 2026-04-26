#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [--check]

Generate Codex agent TOML files from canonical OpenCode agent markdown files.

Options:
  --check   Verify generated output matches committed files without writing.
EOF
}

check_only=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --check)
      check_only=true
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
  shift
done

SCRIPT_DIR=$(dirname "$(realpath "$0")")
REPO_ROOT=$(dirname "$SCRIPT_DIR")
SOURCE_DIR="$REPO_ROOT/opencode/agents"
TARGET_DIR="$REPO_ROOT/codex/agents"

if [ ! -d "$SOURCE_DIR" ]; then
  echo "Source directory not found: $SOURCE_DIR" >&2
  exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
  echo "Target directory not found: $TARGET_DIR" >&2
  exit 1
fi

tmp_dir=$(mktemp -d)
cleanup() {
  rm -rf -- "$tmp_dir"
}
trap cleanup EXIT

shopt -s nullglob
for source in "$SOURCE_DIR"/*.md; do
  name=$(basename -- "$source" .md)
  target="$tmp_dir/$name.toml"

  if ! grep -q '^---$' "$source"; then
    echo "Missing frontmatter markers in $source" >&2
    exit 1
  fi

  description=$(awk '
    BEGIN { in_frontmatter = 0; marker_count = 0 }
    /^---$/ {
      marker_count++
      if (marker_count == 1) {
        in_frontmatter = 1
        next
      }
      if (marker_count == 2) {
        in_frontmatter = 0
        exit
      }
    }
    in_frontmatter && /^description:[[:space:]]*/ {
      sub(/^description:[[:space:]]*/, "")
      print
      exit
    }
  ' "$source")

  if [ -z "$description" ]; then
    echo "Missing description in $source" >&2
    exit 1
  fi

  edit_permission=$(awk '
    BEGIN { in_frontmatter = 0; marker_count = 0; in_permission = 0 }
    /^---$/ {
      marker_count++
      if (marker_count == 1) {
        in_frontmatter = 1
        next
      }
      if (marker_count == 2) {
        in_frontmatter = 0
        exit
      }
    }
    !in_frontmatter { next }
    /^permission:[[:space:]]*$/ {
      in_permission = 1
      next
    }
    in_permission && /^[^[:space:]]/ {
      in_permission = 0
    }
    in_permission && /^[[:space:]]+edit:[[:space:]]*/ {
      sub(/^[[:space:]]+edit:[[:space:]]*/, "")
      print
      exit
    }
  ' "$source")

  sandbox_mode="workspace-write"
  if [ "$edit_permission" = "deny" ]; then
    sandbox_mode="read-only"
  fi

  body=$(awk '
    BEGIN { marker_count = 0 }
    /^---$/ {
      marker_count++
      next
    }
    marker_count >= 2 { print }
  ' "$source")

  if printf '%s' "$body" | grep -q '"""'; then
    echo "Prompt body in $source contains unsupported triple quotes" >&2
    exit 1
  fi

  {
    printf 'name = "%s"\n' "$name"
    printf 'description = "%s"\n' "$description"
    printf 'sandbox_mode = "%s"\n' "$sandbox_mode"
    printf 'developer_instructions = """\n'
    printf '%s\n' "$body"
    printf '"""\n'
  } > "$target"
done
shopt -u nullglob

if [ "$check_only" = true ]; then
  diff -ru -- "$TARGET_DIR" "$tmp_dir"
else
  cp -f -- "$tmp_dir"/*.toml "$TARGET_DIR/"
fi
