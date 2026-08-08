#!/usr/bin/env bash

set -euo pipefail

usage() {
  echo "Usage: $0"
  echo "Installs skills from this repo plus external skills globally via npx skills."
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

echo "Installing ai-tools skills..."
npx skills add https://github.com/bruno303/ai-tools --global --yes

echo "Installing external skills..."
npx skills add https://github.com/obra/superpowers --global --yes --skill using-git-worktrees
npx skills add https://github.com/anthropics/skills --global --yes --skill skill-creator
npx skills add https://github.com/mattpocock/skills --global --yes --skill grill-me
npx skills add https://github.com/juliusbrussee/caveman --global --yes --skill caveman

echo "All skills installed globally"