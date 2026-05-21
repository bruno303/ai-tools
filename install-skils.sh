#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${SCRIPT_DIR}/skills"

usage() {
  echo "Usage: $0 [--clean|-c] <target-directory>"
}

CLEAN_TARGET=false
TARGET_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -c|--clean)
      CLEAN_TARGET=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "Error: unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      if [[ -n "${TARGET_DIR}" ]]; then
        echo "Error: multiple target directories provided" >&2
        usage >&2
        exit 1
      fi

      TARGET_DIR="$1"
      shift
      ;;
  esac
done

if [[ -z "${TARGET_DIR}" ]]; then
  echo "Error: target directory is required" >&2
  usage >&2
  exit 1
fi

if [[ ! -d "${SKILLS_DIR}" ]]; then
  echo "Error: skills directory not found at ${SKILLS_DIR}" >&2
  exit 1
fi

if [[ "${CLEAN_TARGET}" == true && -e "${TARGET_DIR}" ]]; then
  if [[ "${TARGET_DIR}" == "/" ]]; then
    echo "Error: refusing to delete root directory" >&2
    exit 1
  fi

  rm -rf "${TARGET_DIR}"
fi

mkdir -p "${TARGET_DIR}"

for skill_path in "${SKILLS_DIR}"/*; do
  [[ -d "${skill_path}" ]] || continue
  cp -R "${skill_path}" "${TARGET_DIR}/"
done

echo "Skills copied from ${SKILLS_DIR} to ${TARGET_DIR}"

echo "Installing external skills..."
npx skills add https://github.com/obra/superpowers --global --yes --skill using-git-worktrees
npx skills add https://github.com/anthropics/skills --global --yes --skill skill-creator
npx skills add https://github.com/mattpocock/skills --global --yes --skill grill-me
npx skills add https://github.com/juliusbrussee/caveman --global --yes --skill caveman

echo "External skills installed"
