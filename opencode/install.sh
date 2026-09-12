#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [--clean] [--remove-model] <target-dir>
Or set the TARGET_DIR environment variable.
EOF
}

clean_args=()
remove_model=false
target_arg=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --clean|-c) clean_args=(--clean) ;;
    --remove-model) remove_model=true ;;
    --help|-h) usage; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    *)
      if [ -n "$target_arg" ]; then
        echo "Unexpected extra argument: $1" >&2; usage >&2; exit 2
      fi
      target_arg="$1"
      ;;
  esac
  shift
done

target_dir="${target_arg:-${TARGET_DIR:-}}"
if [[ -z "$target_dir" ]]; then
  usage >&2
  exit 2
fi

root_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
target_dir="$(realpath -m -- "$target_dir")"
if [ "$remove_model" = true ]; then
  bash "$root_dir/install-agents.sh" "${clean_args[@]}" opencode "$target_dir"
  temporary_dir="$(mktemp -d)"
  trap 'rm -rf -- "$temporary_dir"' EXIT
  for agent in executor reviewer codebase-reader; do
    awk '!/^[[:space:]]*model:[[:space:]].*$/' \
      "$target_dir/agents/$agent.md" > "$temporary_dir/$agent.md"
    mv -- "$temporary_dir/$agent.md" "$target_dir/agents/$agent.md"
  done
else
  bash "$root_dir/install-agents.sh" "${clean_args[@]}" opencode "$target_dir"
fi
