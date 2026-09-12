#!/usr/bin/env python3
"""Run OpenCode while collecting usage from its JSON event stream."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import subprocess
import sys
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


def write_usage(root_fd: int, components: tuple[str, ...], usage: dict[str, Any]) -> None:
    """Atomically write usage relative to an already-open invocation directory."""
    if not components:
        raise ValueError("usage file must name a file")

    # The caller owns root_fd and keeps it open across the subprocess.
    directory_fds: list[int] = []
    parent_fd = root_fd
    try:
        for component in components[:-1]:
            while True:
                try:
                    child_fd = os.open(
                        component,
                        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                        dir_fd=parent_fd,
                    )
                    break
                except FileNotFoundError:
                    try:
                        os.mkdir(component, dir_fd=parent_fd)
                    except FileExistsError:
                        continue
            directory_fds.append(child_fd)
            parent_fd = child_fd

        filename = components[-1]
        temporary = None
        fd = None
        for _ in range(100):
            temporary = f".{filename}.{os.getpid()}.{secrets.token_hex(8)}"
            try:
                fd = os.open(
                    temporary,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    0o600,
                    dir_fd=parent_fd,
                )
                break
            except FileExistsError:
                continue
        if fd is None or temporary is None:
            raise FileExistsError("could not create a temporary usage file")

        temporary_path = temporary
        assert fd is not None
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                fd = None
                json.dump(usage, handle, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, filename, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        finally:
            if fd is not None:
                os.close(fd)
            try:
                os.unlink(temporary_path, dir_fd=parent_fd)
            except FileNotFoundError:
                pass
    finally:
        for directory_fd in reversed(directory_fds):
            os.close(directory_fd)


def _validate_usage_path(value: str, allowed_directory: Path | None = None) -> Path:
    """Return a usage path constrained to the invocation directory."""
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("usage file must be a relative path without parent traversal")

    directory = (allowed_directory or Path.cwd()).resolve()
    candidate = (directory / path).resolve(strict=False)
    try:
        candidate.relative_to(directory)
    except ValueError as error:
        raise ValueError("usage file must remain within the invocation directory") from error
    return candidate


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

    # Open the directory while it is still the invocation directory.  Keeping
    # this descriptor across the child process prevents a child from replacing
    # the cwd pathname before usage is written.
    invocation_fd = os.open(".", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    invocation_directory = Path.cwd().resolve()
    try:
        usage_path = _validate_usage_path(args.usage_file, invocation_directory)
        usage_components = usage_path.relative_to(invocation_directory).parts
    except ValueError as error:
        os.close(invocation_fd)
        parser.error(str(error))

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
        try:
            write_usage(invocation_fd, usage_components, parse_usage([]))
        finally:
            os.close(invocation_fd)
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

    try:
        write_usage(invocation_fd, usage_components, parse_usage(events))
    finally:
        os.close(invocation_fd)
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
