#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [--clean] <target-dir>
Or set the TARGET_DIR environment variable.

This script installs all files from \`agents/\` into <target-dir>/agents/
and installs each subfolder of \`skills/\` into <target-dir>/skills/<skill-name>/.
Existing files are replaced.

Options:
  --clean, -c  Remove destination \`agents/\` and \`skills/\` before copying.
EOF
}

clean_install=false
target_arg=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --clean|-c)
      clean_install=true
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
  echo "Cleaning destination agents/ and skills/ directories"
  rm -rf -- "$TARGET_DIR/agents" "$TARGET_DIR/skills"
fi

mkdir -p "$TARGET_DIR/agents"
shopt -s nullglob
for f in agents/*.md; do
  if [ -f "$f" ]; then
    cp -f -- "$f" "$TARGET_DIR/agents/"
    echo "Copied $f -> $TARGET_DIR/agents/"
  fi
done
shopt -u nullglob


mkdir -p "$TARGET_DIR/skills"
for d in skills/*; do
  if [ -d "$d" ]; then
    name=$(basename -- "$d")
    dest="$TARGET_DIR/skills/$name"
    mkdir -p "$dest"
    cp -r -- "$d/." "$dest/"
    echo "Copied $d -> $dest/"
  fi
done

echo "Done."
