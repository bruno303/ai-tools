#!/usr/bin/env python3
"""Verify that OpenCode discovered the workspace-local benchmark config."""

from __future__ import annotations

import subprocess
import sys
import json
from pathlib import Path

EXPECTED_PERMISSIONS = (
    {"action": "external_directory", "resource": "$HOME/.agents/skills/*", "effect": "allow"},
    {"action": "read", "resource": "$HOME/.agents/skills/*", "effect": "allow"},
)


def main() -> int:
    config = Path.cwd() / "opencode.jsonc"
    if not config.is_file():
        print(f"missing workspace config: {config}", file=sys.stderr)
        return 1
    try:
        completed = subprocess.run(
            ["opencode2", "debug", "config"],
            cwd=Path.cwd(), capture_output=True, text=True, check=False
        )
    except OSError as error:
        print(f"could not run opencode2 debug config: {error}", file=sys.stderr)
        return 1
    output = f"{completed.stdout}\n{completed.stderr}"
    if completed.returncode != 0:
        print(output, file=sys.stderr, end="")
        return completed.returncode or 1
    try:
        debug_config = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        print(f"could not parse opencode2 debug config JSON: {error}", file=sys.stderr)
        print(output, file=sys.stderr, end="")
        return 1

    expected_path = config.resolve()

    def has_workspace_document(value: object) -> bool:
        if isinstance(value, dict):
            path = value.get("path")
            if value.get("type") == "document" and isinstance(path, str):
                try:
                    if Path(path).resolve() == expected_path:
                        info = value.get("info")
                        permissions = info.get("permissions") if isinstance(info, dict) else None
                        if not isinstance(permissions, list) or not permissions:
                            return False
                        if any(
                            not isinstance(permission, dict)
                            or set(permission) != {"action", "resource", "effect"}
                            or not all(isinstance(permission[field], str) for field in ("action", "resource", "effect"))
                            for permission in permissions
                        ):
                            return False
                        return all(permission in permissions for permission in EXPECTED_PERMISSIONS)
                except OSError:
                    return False
            return any(has_workspace_document(item) for item in value.values())
        if isinstance(value, list):
            return any(has_workspace_document(item) for item in value)
        return False

    if not has_workspace_document(debug_config):
        print("workspace-local opencode.jsonc was not reported as a discovered document", file=sys.stderr)
        print(output, file=sys.stderr, end="")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
