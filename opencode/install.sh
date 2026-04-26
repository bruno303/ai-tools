#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [--clean] [--remove-model] <target-dir>
Or set the TARGET_DIR environment variable.

This script installs all files from \`agents/\` into <target-dir>/agents/
Existing files are replaced.

Options:
  --clean, -c         Remove destination \`agents/\` before copying.
  --remove-model      Remove any \`model: ...\` line from installed agent frontmatter.
EOF
}

clean_install=false
remove_model=false
target_arg=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --clean|-c)
      clean_install=true
      ;;
    --remove-model)
      remove_model=true
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
    *)
      if [ -n "$target_arg" ]; then
        echo "Unexpected extra argument: $1" >&2
        usage
        exit 2
      fi
      target_arg="$1"
      ;;
  esac
  shift
done

TARGET_DIR="${target_arg:-${TARGET_DIR:-}}"
if [ -z "$TARGET_DIR" ]; then
  usage
  exit 2
fi

TARGET_DIR=$(realpath "$TARGET_DIR")

echo "Target directory: $TARGET_DIR"

if [ "$clean_install" = true ]; then
  echo "Cleaning destination agents/ directory"
  rm -rf -- "$TARGET_DIR/agents"
fi

mkdir -p "$TARGET_DIR/agents"
shopt -s nullglob
for f in agents/*.md; do
  if [ -f "$f" ]; then
    dest="$TARGET_DIR/agents/$(basename -- "$f")"
    if [ "$remove_model" = true ]; then
      awk '!/^[[:space:]]*model:[[:space:]].*$/' "$f" > "$dest"
    else
      cp -f -- "$f" "$dest"
    fi
    echo "Copied $f -> $TARGET_DIR/agents/"
  fi
done
shopt -u nullglob

echo "Done."
