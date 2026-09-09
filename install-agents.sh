#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [--clean] <opencode|codex|claude> <target-dir>

Copy the active executor and reviewer definitions for a harness.
EOF
}

clean_install=false
if [[ "${1:-}" = "--clean" ]]; then
  clean_install=true
  shift
fi

if [[ "$#" -ne 2 ]]; then
  echo "Expected a harness and target directory." >&2
  usage >&2
  exit 2
fi

harness="$1"
target_arg="$2"
case "$harness" in
  opencode)
    destination_suffix="agents"
    agent_extension="md"
    ;;
  codex)
    destination_suffix=".codex/agents"
    agent_extension="toml"
    ;;
  claude)
    destination_suffix=".claude/agents"
    agent_extension="md"
    ;;
  *)
    echo "Unknown harness: $harness (expected opencode, codex, or claude)." >&2
    exit 2
    ;;
esac

if [[ -z "$target_arg" || "$target_arg" == -* ]]; then
  echo "Invalid target directory: $target_arg" >&2
  exit 2
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
target_dir="$(realpath -m -- "$target_arg")"
source_dir="$script_dir/$harness/agents"
destination_dir="$target_dir/$destination_suffix"
source_dir="$(realpath -m -- "$source_dir")"
destination_dir="$(realpath -m -- "$destination_dir")"

if [[ ! -d "$source_dir" ]]; then
  echo "Missing install source: $source_dir" >&2
  exit 1
fi

if [[ "$clean_install" = true ]]; then
  if [[ "$target_dir" = "/" || "$target_dir" = "$script_dir" ]]; then
    echo "Refusing to clean unsafe target directory: $target_dir" >&2
    exit 2
  fi
  if [[ "$destination_dir" = "$source_dir" ]] \
    || [[ "$destination_dir" == "$source_dir"/* ]] \
    || [[ "$source_dir" == "$destination_dir"/* ]]; then
    echo "Refusing to clean destination overlapping install source: $destination_dir" >&2
    exit 2
  fi
fi

if [[ "$clean_install" = true ]]; then
  rm -rf -- "$destination_dir"
fi
mkdir -p -- "$destination_dir"
cp -- "$source_dir/executor.$agent_extension" "$destination_dir/"
cp -- "$source_dir/reviewer.$agent_extension" "$destination_dir/"

echo "Installed $harness agents in $destination_dir"
