#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 <target-dir>
Or set the TARGET_DIR environment variable.

This script copies all files from `agents/` into <target-dir>/agents/
and copies each subfolder of `skills/` into <target-dir>/skills/<skill-name>/.
Existing files are replaced.
EOF
}

TARGET_DIR="${1:-${TARGET_DIR:-}}"
if [ -z "$TARGET_DIR" ]; then
  usage
  exit 2
fi

TARGET_DIR=$(realpath "$TARGET_DIR")

echo "Target directory: $TARGET_DIR"

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
