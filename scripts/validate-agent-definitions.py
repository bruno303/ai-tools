#!/usr/bin/env python3
"""Validate the active executor/reviewer definitions for all supported harnesses."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path
from typing import Any


EXPECTED = {
    "opencode": {
        "files": {"executor.md", "reviewer.md"},
        "format": "frontmatter",
        "required": {
            "executor": {
                "mode": "subagent",
                "model": None,
                "reasoningEffort": None,
            },
            "reviewer": {
                "mode": "subagent",
                "model": None,
                "reasoningEffort": None,
            },
        },
    },
    "codex": {
        "files": {"executor.toml", "reviewer.toml"},
        "format": "toml",
        "required": {
            "executor": {
                "name": "executor",
                "description": None,
                "model": None,
                "model_reasoning_effort": None,
                "developer_instructions": "",
            },
            "reviewer": {
                "name": "reviewer",
                "description": None,
                "model": None,
                "model_reasoning_effort": None,
                "developer_instructions": "",
            },
        },
    },
    "claude": {
        "files": {"executor.md", "reviewer.md"},
        "format": "frontmatter",
        "required": {
            "executor": {
                "name": "executor",
                "description": None,
                "model": None,
            },
            "reviewer": {
                "name": "reviewer",
                "description": None,
                "model": None,
            },
        },
    },
}

KEY_PATTERN = re.compile(r"(?P<key>[A-Za-z_][A-Za-z0-9_-]*):")


def _parse_scalar(value: str, line_number: int) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"line {line_number}: expected a scalar value")
    if value[0] in "'\"":
        if len(value) < 2 or value[-1] != value[0]:
            raise ValueError(f"line {line_number}: unterminated quoted value")
        if value[0] == "'":
            return value[1:-1].replace("''", "'")
        return value[1:-1].replace('\\"', '"').replace('\\\\', '\\')
    return value


def _find_frontmatter_end(lines: list[str]) -> int:
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening frontmatter delimiter")
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return index
    raise ValueError("missing closing frontmatter delimiter")


def _parse_frontmatter_line(line: str, line_number: int) -> tuple[int, str, str]:
    indentation = line[: len(line) - len(line.lstrip(" "))]
    if "\t" in indentation:
        raise ValueError(f"line {line_number}: tabs are not valid indentation")
    indent = len(indentation)
    content = line[indent:]
    match = KEY_PATTERN.match(content)
    if not match:
        raise ValueError(f"line {line_number}: expected a mapping entry")
    return indent, match.group("key"), content[match.end() :]


def _parse_frontmatter_mapping(lines: list[str]) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    last_indent = -1
    last_created_mapping = True

    for line_number, line in enumerate(lines, start=2):
        if not line.strip():
            continue
        indent, key, raw_value = _parse_frontmatter_line(line, line_number)
        if indent > last_indent and not last_created_mapping:
            raise ValueError(f"line {line_number}: unexpected indentation")
        while indent <= stack[-1][0]:
            stack.pop()
        mapping = stack[-1][1]
        if key in mapping:
            raise ValueError(f"line {line_number}: duplicate key {key!r}")
        if not raw_value.strip():
            value: Any = {}
            last_created_mapping = True
        else:
            value = _parse_scalar(raw_value, line_number)
            last_created_mapping = False
        mapping[key] = value
        last_indent = indent
        if last_created_mapping:
            stack.append((indent, value))

    return root


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse the small YAML mapping used by the repository's agent headers."""

    lines = text.splitlines()
    end = _find_frontmatter_end(lines)
    root = _parse_frontmatter_mapping(lines[1:end])
    if not root:
        raise ValueError("frontmatter must contain at least one field")
    if any(line.strip() for line in lines[end + 1 :]):
        raise ValueError("agent body must be empty")
    return root


def _validate_fields(value: Any, expected: dict[str, Any], path: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected a mapping")
        return
    for key, requirement in expected.items():
        field_path = f"{path}.{key}"
        if key not in value:
            errors.append(f"{field_path}: missing required field")
            continue
        actual = value[key]
        if isinstance(requirement, dict):
            _validate_fields(actual, requirement, field_path, errors)
        elif requirement is None:
            if not isinstance(actual, str) or not actual.strip():
                errors.append(f"{field_path}: expected a non-empty string")
        elif actual != requirement:
            errors.append(f"{field_path}: expected {requirement!r}, found {actual!r}")


def _parse_definition(path: Path, definition_format: str) -> tuple[dict[str, Any] | None, str | None]:
    text = path.read_text(encoding="utf-8")
    try:
        if definition_format == "toml":
            value = tomllib.loads(text)
            if not isinstance(value, dict):
                return None, "top-level value must be a table"
            return value, None
        return parse_frontmatter(text), None
    except ValueError as exc:
        return None, str(exc)


def validate_harness(root: Path, harness: str) -> list[str]:
    directory = root / harness / "agents"
    expected = EXPECTED[harness]
    errors: list[str] = []
    if not directory.is_dir():
        return [f"{harness}: missing directory {directory}"]
    actual = {path.name for path in directory.iterdir()}
    if actual != expected["files"]:
        errors.append(f"{harness}: expected files {sorted(expected['files'])}, found {sorted(actual)}")

    suffix = ".toml" if expected["format"] == "toml" else ".md"
    for role, required in expected["required"].items():
        path = directory / f"{role}{suffix}"
        if not path.is_file():
            continue
        parsed, parse_error = _parse_definition(path, expected["format"])
        if parse_error is not None:
            errors.append(f"{path}: malformed {expected['format']} configuration: {parse_error}")
            continue
        _validate_fields(parsed, required, str(path), errors)
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = [error for harness in EXPECTED for error in validate_harness(root, harness)]
    if errors:
        print("Agent definition validation failed:", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print("Agent definitions are valid for opencode, codex, and claude.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
