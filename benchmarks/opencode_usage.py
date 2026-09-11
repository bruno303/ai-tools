#!/usr/bin/env python3
"""Run OpenCode while collecting usage from its JSON event stream."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from typing import Any, Iterable, TextIO


MODEL_EVENT_TYPES = {"step_finish"}
SUBAGENT_EVENT_TYPES = {"tool_use"}


def _number(mapping: dict[str, Any], *names: str) -> int | float:
    for name in names:
        value = mapping.get(name)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return value
    return 0


def _payload(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("part")
    return payload if isinstance(payload, dict) else {}


def parse_usage(events: Iterable[dict[str, Any]]) -> dict[str, int | float]:
    """Aggregate the usage fields emitted by OpenCode model events.

    OpenCode has added fields to event payloads over time, so this deliberately
    reads only known fields and ignores everything else.
    """
    usage: dict[str, int | float] = {
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "model_calls": 0,
        "subagent_calls": 0,
        "cost": 0,
    }
    for event in events:
        event_type = event.get("type")
        payload = _payload(event)
        if event_type in MODEL_EVENT_TYPES:
            tokens = payload.get("tokens")
            if not isinstance(tokens, dict):
                tokens = {}
            cache = tokens.get("cache") if isinstance(tokens.get("cache"), dict) else {}
            usage["input_tokens"] += _number(tokens, "input", "input_tokens")
            usage["cached_input_tokens"] += _number(cache, "read", "cached_input", "cached_input_tokens")
            usage["output_tokens"] += _number(tokens, "output", "output_tokens")
            usage["model_calls"] += 1
            cost = payload.get("cost")
            if isinstance(cost, (int, float)) and not isinstance(cost, bool):
                usage["cost"] += cost

        if event_type in SUBAGENT_EVENT_TYPES and payload.get("tool") == "task":
            usage["subagent_calls"] += 1

    return usage


def aggregate_usage(events: Iterable[dict[str, Any]]) -> dict[str, int | float]:
    return parse_usage(events)


def write_usage(path: Path, usage: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(usage, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--usage-file", default=".benchmark-usage.json")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = list(args.command)
    if command[:1] == ["--"]:
        command.pop(0)
    if not command:
        command = ["opencode", "run", "--format", "json"]
    if command[:2] == ["opencode", "run"] and "--format" not in command:
        command[2:2] = ["--format", "json"]

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
    except OSError as error:
        print(f"opencode wrapper: {error}", file=sys.stderr)
        write_usage(Path(args.usage_file), parse_usage([]))
        return 127

    events: list[dict[str, Any]] = []

    def consume_stdout(stream: TextIO) -> None:
        for line in stream:
            sys.stdout.write(line)
            sys.stdout.flush()
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                events.append(event)

    def consume_stderr(stream: TextIO) -> None:
        for line in stream:
            sys.stderr.write(line)
            sys.stderr.flush()

    assert process.stdout is not None
    assert process.stderr is not None
    stdout_thread = threading.Thread(target=consume_stdout, args=(process.stdout,))
    stderr_thread = threading.Thread(target=consume_stderr, args=(process.stderr,))
    stdout_thread.start()
    stderr_thread.start()
    returncode = process.wait()
    stdout_thread.join()
    stderr_thread.join()
    process.stdout.close()
    process.stderr.close()

    write_usage(Path(args.usage_file), parse_usage(events))
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
