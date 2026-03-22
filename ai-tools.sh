#!/bin/bash

opencode-run() {
  docker run --rm -it \
    -v "$PWD":"$PWD" \
    -w "$PWD" \
    -v "$HOME/.config/opencode:/root/.config/opencode" \
    -v "$HOME/.local/share/opencode:/root/.local/share/opencode" \
    -v "$HOME/.local/state/opencode:/root/.local/state/opencode" \
    ghcr.io/anomalyco/opencode:latest "$@"
}
