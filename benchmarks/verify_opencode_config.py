#!/usr/bin/env python3
"""Verify that OpenCode discovered the workspace-local benchmark config."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Iterator

EXPECTED_PERMISSIONS = (
    {"action": "external_directory", "resource": "$HOME/.agents/skills/*", "effect": "allow"},
    {"action": "read", "resource": "$HOME/.agents/skills/*", "effect": "allow"},
)


def iter_mappings(value: object) -> Iterator[dict[str, object]]:
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from iter_mappings(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_mappings(item)


def has_expected_permissions(document: dict[str, object]) -> bool:
    info = document.get("info")
    permissions = info.get("permissions") if isinstance(info, dict) else None
    if not isinstance(permissions, list) or not permissions:
        return False
    if not all(is_valid_permission(permission) for permission in permissions):
        return False
    return all(permission in permissions for permission in EXPECTED_PERMISSIONS)


def is_valid_permission(permission: object) -> bool:
    return (
        isinstance(permission, dict)
        and set(permission) == {"action", "resource", "effect"}
        and all(isinstance(permission[field], str) for field in ("action", "resource", "effect"))
    )


def is_workspace_document(document: dict[str, object], expected_path: Path) -> bool:
    path = document.get("path")
    if document.get("type") != "document" or not isinstance(path, str):
        return False
    try:
        return Path(path).resolve() == expected_path and has_expected_permissions(document)
    except OSError:
        return False


def has_workspace_document(debug_config: object, expected_path: Path) -> bool:
    return any(is_workspace_document(document, expected_path) for document in iter_mappings(debug_config))


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

    if not has_workspace_document(debug_config, config.resolve()):
        print("workspace-local opencode.jsonc was not reported as a discovered document", file=sys.stderr)
        print(output, file=sys.stderr, end="")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
