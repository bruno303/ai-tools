#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import selectors
import shlex
import shutil
import signal
import statistics
import subprocess
import tempfile
import time
import hashlib
import re
import errno
import fcntl
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = ROOT.parent
RESULTS_DIR = ROOT / "results"
DURATION_SECONDS = "duration_seconds"
INPUT_TOKENS = "input_tokens"
GIT_IDENTITY_NAME = "benchmark"
GIT_IDENTITY_EMAIL = "benchmark@localhost"
RESULT_COUNTER = 0
EXTERNAL_FIXTURE_CACHE = Path(os.environ.get("BENCHMARK_FIXTURE_CACHE", Path.home() / ".cache" / "ai-tools-benchmark"))


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_timestamp(value: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected an ISO-8601 timestamp") from error
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise argparse.ArgumentTypeError("timestamp must include a timezone")
    return timestamp.astimezone(timezone.utc)


def normalize_command(command: str | list[str]) -> list[str]:
    if isinstance(command, str):
        return shlex.split(command)
    return [str(part) for part in command]


def render_command(command: str | list[str], task_path: Path, workspace: Path) -> list[str]:
    task_content = task_path.read_text(encoding="utf-8")
    replacements = {
        "{repository_root}": str(REPOSITORY_ROOT),
        "{task_file}": str(task_path),
        "{workspace}": str(workspace),
        "{task_content}": task_content,
    }
    rendered: list[str] = []
    for part in normalize_command(command):
        for placeholder, value in replacements.items():
            part = part.replace(placeholder, value)
        rendered.append(part)
    return rendered


def command_result(
    command: list[str],
    started: float,
    exit_code: int | None,
    stdout: str,
    stderr: str,
    timed_out: bool,
) -> dict[str, Any]:
    return {
        "command": command,
        "exit_code": exit_code,
        DURATION_SECONDS: round(time.monotonic() - started, 3),
        "stdout": stdout,
        "stderr": stderr,
        "timed_out": timed_out,
    }


def terminate_process_group(process: subprocess.Popen[str]) -> None:
    process_group = process.pid
    if process_group == os.getpgrp():
        return
    try:
        os.killpg(process_group, signal.SIGTERM)
    except ProcessLookupError:
        return

    deadline = time.monotonic() + 1
    while time.monotonic() < deadline:
        time.sleep(0.05)
    try:
        os.killpg(process_group, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        process.wait()
    except ProcessLookupError:
        pass


def emit_heartbeat(
    started: float,
    now: float,
    timeout: int | None,
    next_heartbeat: float,
    quiet: bool,
    verbose: bool,
) -> float:
    if not quiet and not verbose and now >= next_heartbeat:
        heartbeat = f"running {int(now - started)}s / {timeout}s"
        if os.isatty(2):
            print(f"\r{heartbeat}", end="", file=os.sys.stderr, flush=True)
        else:
            print(heartbeat, file=os.sys.stderr, flush=True)
        return now + 15
    return next_heartbeat


def read_ready_events(
    selector: selectors.BaseSelector,
    output: dict[str, bytearray],
    verbose: bool,
    quiet: bool,
    timeout: float,
) -> None:
    for key, _ in selector.select(timeout=timeout):
        data = os.read(key.fileobj.fileno(), 65536)
        if not data:
            selector.unregister(key.fileobj)
            continue
        stream = key.data
        output[stream].extend(data)
        if verbose and not quiet:
            text = data.decode(errors="replace")
            for line in text.splitlines(True):
                print(f"[{stream}] {line}", end="", file=os.sys.stderr, flush=True)


def drain_output(
    selector: selectors.BaseSelector,
    output: dict[str, bytearray],
    verbose: bool,
    quiet: bool,
) -> None:
    drain_deadline = time.monotonic() + 1
    while selector.get_map() and time.monotonic() < drain_deadline:
        read_ready_events(selector, output, verbose, quiet, timeout=0.05)


def run_command(
    command: list[str],
    cwd: Path,
    env: dict[str, str],
    timeout: int | None,
    quiet: bool = False,
    verbose: bool = False,
) -> dict[str, Any]:
    started = time.monotonic()
    process = subprocess.Popen(  # NOSONAR
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    selector = selectors.DefaultSelector()
    assert process.stdout is not None
    assert process.stderr is not None
    selector.register(process.stdout, selectors.EVENT_READ, "stdout")
    selector.register(process.stderr, selectors.EVENT_READ, "stderr")
    output = {"stdout": bytearray(), "stderr": bytearray()}
    next_heartbeat = started + 15
    timed_out = False
    try:
        while process.poll() is None:
            now = time.monotonic()
            if timeout is not None and now - started >= timeout:
                timed_out = process.poll() is None
                break
            next_heartbeat = emit_heartbeat(started, now, timeout, next_heartbeat, quiet, verbose)
            read_ready_events(selector, output, verbose, quiet, timeout=0.2)
    finally:
        terminate_process_group(process)
        drain_output(selector, output, verbose, quiet)
        selector.close()
        process.stdout.close()
        process.stderr.close()
        process.wait()
    if os.isatty(2) and not quiet and not verbose:
        print("\r" + " " * 40 + "\r", end="", file=os.sys.stderr, flush=True)
    return command_result(
        command,
        started,
        None if timed_out else process.returncode,
        bytes(output["stdout"]).decode(errors="replace"),
        bytes(output["stderr"]).decode(errors="replace"),
        timed_out,
    )


def step_passed(step: dict[str, Any]) -> bool:
    return step["exit_code"] == 0 and not step["timed_out"]


def init_workspace_repo(workspace: Path) -> None:
    # Best-effort: make each workspace its own self-contained git repository so
    # harness tooling roots itself inside the sandbox instead of climbing to (or
    # binding to) an enclosing repository and mutating real files. Failures are
    # ignored so a missing git binary never breaks an execution.
    git_env = os.environ.copy()
    git_env.update(
        {
            "GIT_AUTHOR_NAME": GIT_IDENTITY_NAME,
            "GIT_AUTHOR_EMAIL": GIT_IDENTITY_EMAIL,
            "GIT_COMMITTER_NAME": GIT_IDENTITY_NAME,
            "GIT_COMMITTER_EMAIL": GIT_IDENTITY_EMAIL,
        }
    )
    try:
        subprocess.run(["git", "init", "-q"], cwd=workspace, env=git_env, capture_output=True, timeout=30, check=False)
        subprocess.run(
            ["git", "config", "user.name", GIT_IDENTITY_NAME], cwd=workspace, env=git_env, capture_output=True, timeout=30, check=False
        )
        subprocess.run(
            ["git", "config", "user.email", GIT_IDENTITY_EMAIL], cwd=workspace, env=git_env, capture_output=True, timeout=30, check=False
        )
        subprocess.run(["git", "add", "-A"], cwd=workspace, env=git_env, capture_output=True, timeout=30, check=False)
        subprocess.run(
            ["git", "commit", "-q", "-m", "scenario fixture"], cwd=workspace, env=git_env, capture_output=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError):
        pass


def _external_fixture_config(fixture: Any) -> tuple[str, str]:
    if not isinstance(fixture, dict):
        raise ValueError("external fixture must be an object")
    url = fixture.get("url", fixture.get("git_url", fixture.get("git")))
    revision = fixture.get("commit", fixture.get("commit_sha", fixture.get("revision", fixture.get("sha"))))
    if not isinstance(url, str) or not url:
        raise ValueError("external fixture requires a Git URL")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
        raise ValueError("external fixture requires a full 40-character commit SHA")
    return url, revision.lower()


def _verify_pinned_checkout(checkout: Path, revision: str) -> bool:
    """Require the pinned commit and a completely clean checkout."""
    object_type = subprocess.run(
        ["git", "cat-file", "-t", revision], cwd=checkout, capture_output=True, text=True, timeout=30, check=False
    )
    if object_type.returncode != 0 or object_type.stdout.strip() != "commit":
        return False
    resolved = subprocess.run(
        ["git", "rev-parse", "--verify", f"{revision}^{{commit}}"],
        cwd=checkout, capture_output=True, text=True, timeout=30, check=False,
    )
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=checkout, capture_output=True, text=True, timeout=30, check=False
    )
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all", "--ignored"],
        cwd=checkout,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return (
        resolved.returncode == 0
        and resolved.stdout.strip().lower() == revision
        and head.returncode == 0
        and head.stdout.strip().lower() == revision
        and status.returncode == 0
        and not status.stdout
    )


def materialize_external_fixture(fixture: dict[str, Any]) -> tuple[Path, dict[str, str]]:
    """Return a cached, pinned checkout. The returned directory must not be modified."""
    url, revision = _external_fixture_config(fixture)
    key = hashlib.sha256(f"{url}\0{revision}".encode()).hexdigest()
    cache = Path(os.environ.get("BENCHMARK_FIXTURE_CACHE", str(EXTERNAL_FIXTURE_CACHE)))
    checkout = cache / key
    cache.mkdir(parents=True, exist_ok=True)
    lock = cache / f".{key}.lock"
    # flock is released by the kernel when the owning process exits, including
    # an ungraceful termination.  Keep the lock file itself persistent so a
    # waiter never has to guess whether a directory lock's owner is stale.
    with lock.open("a+") as lock_handle:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        try:
            if (checkout / ".git").is_dir() and _verify_pinned_checkout(checkout, revision):
                return checkout, {"url": url, "commit": revision}
            temporary = Path(tempfile.mkdtemp(prefix=f".{key}-", dir=cache))
            backup: Path | None = None
            try:
                clone = subprocess.run(["git", "clone", "--quiet", url, str(temporary)], capture_output=True, text=True, timeout=300, check=False)
                if clone.returncode != 0:
                    raise RuntimeError(clone.stderr.strip() or "git clone failed")
                checkout_result = subprocess.run(["git", "checkout", "--quiet", "--detach", revision], cwd=temporary, capture_output=True, text=True, timeout=300, check=False)
                if checkout_result.returncode != 0:
                    raise RuntimeError(checkout_result.stderr.strip() or "pinned revision was not found")
                if not _verify_pinned_checkout(temporary, revision):
                    raise RuntimeError("requested revision did not resolve to the checked-out commit")
                if checkout.exists():
                    backup = cache / f".{key}-old-{os.getpid()}"
                    checkout.replace(backup)
                temporary.replace(checkout)
                temporary = checkout
                if backup is not None:
                    shutil.rmtree(backup, ignore_errors=True)
            except OSError as error:
                if error.errno not in (errno.EEXIST, errno.ENOTEMPTY):
                    raise
                if not _verify_pinned_checkout(checkout, revision):
                    raise RuntimeError("concurrent cache publication is invalid")
            except Exception:
                shutil.rmtree(temporary, ignore_errors=True)
                raise
        finally:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
    return checkout, {"url": url, "commit": revision}


def fixture_source(scenario_dir: Path, fixture: Any) -> tuple[Path, dict[str, str] | None]:
    if isinstance(fixture, str):
        return scenario_dir / fixture, None
    source, provenance = materialize_external_fixture(fixture)
    return source, provenance


def _safe_relative_path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError(f"{label} must be a relative path")
    path = Path(value)
    if ".." in path.parts:
        raise ValueError(f"{label} must stay within the scenario")
    return path


def _validate_fixture_links(source: Path) -> None:
    root = source.resolve()
    for directory, directories, files in os.walk(source, followlinks=False):
        entries = [Path(directory, name) for name in directories + files]
        for entry in entries:
            if entry.is_symlink():
                target = entry.resolve(strict=False)
                try:
                    target.relative_to(root)
                except ValueError as error:
                    raise ValueError(f"fixture symlink escapes checkout: {entry}") from error


def _validate_scenario(scenario: dict[str, Any], scenario_dir: Path) -> None:
    if not isinstance(scenario, dict) or not isinstance(scenario.get("name"), str) or not scenario["name"]:
        raise ValueError("scenario name must be a non-empty string")
    fixture = scenario.get("fixture")
    if isinstance(fixture, str):
        fixture_path = scenario_dir / _safe_relative_path(fixture, "fixture")
        if not fixture_path.exists() or not fixture_path.is_dir():
            raise ValueError("fixture must name an existing directory")
        try:
            fixture_path.resolve().relative_to(scenario_dir.resolve())
        except ValueError as error:
            raise ValueError("fixture must stay within the scenario") from error
    elif isinstance(fixture, dict):
        _external_fixture_config(fixture)
    else:
        raise ValueError("fixture must be a relative directory or external fixture object")
    task = scenario.get("task")
    task_path = scenario_dir / _safe_relative_path(task, "task")
    if not task_path.is_file():
        raise ValueError("task must name an existing file")
    timeout = scenario.get("timeout_seconds", 900)
    if isinstance(timeout, bool) or not isinstance(timeout, int) or timeout <= 0:
        raise ValueError("timeout_seconds must be a positive integer")
    token_qualification(scenario, None)
    injections = scenario.get("inject_after_run", [])
    if not isinstance(injections, list):
        raise ValueError("inject_after_run must be a list")
    for injection in injections:
        if not isinstance(injection, dict):
            raise ValueError("each injection must be an object")
        source = scenario_dir / _safe_relative_path(injection.get("source"), "injection source")
        _safe_relative_path(injection.get("destination"), "injection destination")
        if not source.exists():
            raise ValueError("injection source must exist")
    verification = scenario.get("verification", [])
    if not isinstance(verification, list):
        raise ValueError("verification must be a list")
    for evaluation in verification:
        if not isinstance(evaluation, dict) or not isinstance(evaluation.get("name"), str) or not evaluation["name"]:
            raise ValueError("each verification must have a name")
        command = evaluation.get("command")
        if not isinstance(command, (str, list)) or not command or (isinstance(command, list) and not all(isinstance(part, str) for part in command)):
            raise ValueError("each verification command must be a string or argument list")
        evaluation_timeout = evaluation.get("timeout_seconds", timeout)
        if isinstance(evaluation_timeout, bool) or not isinstance(evaluation_timeout, int) or evaluation_timeout <= 0:
            raise ValueError("verification timeout_seconds must be a positive integer")


def token_qualification(scenario: dict[str, Any], usage: dict[str, Any] | None) -> dict[str, Any] | None:
    config = scenario.get("token_target", scenario.get("token_qualification", scenario.get("qualification")))
    if config is None and "minimum_input_tokens" in scenario:
        config = {"metric": INPUT_TOKENS, "minimum": scenario["minimum_input_tokens"]}
    if config is None:
        return None
    if isinstance(config, int):
        config = {"metric": INPUT_TOKENS, "minimum": config}
    if not isinstance(config, dict) or config.get("metric", INPUT_TOKENS) != INPUT_TOKENS:
        raise ValueError("token target metric must be input_tokens")
    minimum = config.get("minimum", config.get("min", config.get("minimum_input_tokens")))
    if not isinstance(minimum, int) or minimum < 0:
        raise ValueError("token target minimum must be a non-negative integer")
    actual = usage.get(INPUT_TOKENS) if isinstance(usage, dict) else None
    if not isinstance(actual, (int, float)) or isinstance(actual, bool):
        actual = None
    return {"metric": INPUT_TOKENS, "minimum": minimum, "actual": actual, "met": actual is not None and actual >= minimum}


def _open_injection_parent(root_fd: int, components: tuple[str, ...]) -> tuple[int, list[int]]:
    directory_fds: list[int] = []
    parent_fd = root_fd
    for component in components[:-1]:
        while True:
            try:
                child_fd = os.open(
                    component,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
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
    return parent_fd, directory_fds


def _copy_injection_file(source: Path, parent_fd: int, filename: str) -> None:
    temporary_name = f".{filename}.{os.getpid()}.{next(tempfile._get_candidate_names())}"
    temporary_fd = os.open(
        temporary_name,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
        0o600,
        dir_fd=parent_fd,
    )
    try:
        shutil.copy2(source, f"/proc/self/fd/{temporary_fd}", follow_symlinks=False)
        try:
            existing = os.stat(filename, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            existing = None
        if existing is not None and stat.S_ISLNK(existing.st_mode):
            raise ValueError(f"injection destination is a symlink: {filename}")
        os.replace(temporary_name, filename, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
    finally:
        os.close(temporary_fd)
        try:
            os.unlink(temporary_name, dir_fd=parent_fd)
        except FileNotFoundError:
            pass


def inject_after_run(scenario_dir: Path, workspace: Path, injections: list[dict[str, str]], workspace_fd: int | None = None) -> None:
    owned_fd = workspace_fd is None
    root_fd = workspace_fd if workspace_fd is not None else os.open(workspace, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    workspace = workspace.absolute()
    try:
        for injection in injections:
            source = scenario_dir / injection["source"]
            destination = workspace / injection["destination"]
            destination_parts = destination.relative_to(workspace).parts
            if source.is_dir():
                for directory, directories, files in os.walk(source, followlinks=False):
                    relative = Path(directory).relative_to(source)
                    target_parts = destination_parts + relative.parts
                    parent_fd, directory_fds = _open_injection_parent(root_fd, target_parts + (".",))
                    try:
                        target_name = target_parts[-1] if target_parts else "."
                        if target_name == ".":
                            target_fd = parent_fd
                        else:
                            try:
                                target_fd = os.open(target_name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
                            except FileNotFoundError:
                                os.mkdir(target_name, dir_fd=parent_fd)
                                target_fd = os.open(target_name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
                        if target_fd != parent_fd:
                            directory_fds.append(target_fd)
                    finally:
                        for fd in reversed(directory_fds):
                            os.close(fd)
                    target_directory = destination / relative
                    _validate_injection_destination(workspace, target_directory, directory=True)
                    for name in directories:
                        _validate_injection_destination(workspace, target_directory / name, directory=True)
                    for name in files:
                        target = target_directory / name
                        _validate_injection_destination(workspace, target)
                        parent_fd, fds = _open_injection_parent(root_fd, (destination_parts + relative.parts + (name,)))
                        try:
                            _copy_injection_file(Path(directory) / name, parent_fd, name)
                        finally:
                            for fd in reversed(fds):
                                os.close(fd)
            else:
                parent_fd, fds = _open_injection_parent(root_fd, destination_parts)
                try:
                    _copy_injection_file(source, parent_fd, destination_parts[-1])
                finally:
                    for fd in reversed(fds):
                        os.close(fd)
    finally:
        if owned_fd:
            os.close(root_fd)


def _validate_injection_destination(workspace: Path, destination: Path, directory: bool = False) -> None:
    try:
        destination.relative_to(workspace)
    except ValueError as error:
        raise ValueError("injection destination must stay within workspace") from error


def collect_usage(variant: dict[str, Any], workspace: Path) -> dict[str, Any] | None:
    usage_path = variant.get("usage_file")
    if not usage_path:
        return None
    path = workspace / usage_path
    if not path.exists():
        return None
    return load_json(path)


def run_setup(
    variant: dict[str, Any],
    task_path: Path,
    workspace: Path,
    env: dict[str, str],
    timeout: int,
    quiet: bool,
    verbose: bool,
) -> tuple[list[dict[str, Any]], bool]:
    steps: list[dict[str, Any]] = []
    for command in variant.get("setup", []):
        step = run_command(render_command(command, task_path, workspace), workspace, env, timeout, quiet, verbose)
        steps.append(step)
        if not step_passed(step):
            return steps, False
    return steps, True


def run_verifications(
    scenario: dict[str, Any],
    task_path: Path,
    workspace: Path,
    env: dict[str, str],
    timeout: int,
    quiet: bool,
    verbose: bool,
) -> tuple[list[dict[str, Any]], bool]:
    steps: list[dict[str, Any]] = []
    all_passed = True
    for evaluation in scenario.get("verification", []):
        command = render_command(evaluation["command"], task_path, workspace)
        step = run_command(
            command,
            workspace,
            env,
            int(evaluation.get("timeout_seconds", timeout)),
            quiet,
            verbose,
        )
        step["name"] = evaluation["name"]
        step["passed"] = step_passed(step)
        steps.append(step)
        all_passed = all_passed and step["passed"]
    return steps, all_passed


def execute_scenario(
    scenario_path: Path,
    variant_path: Path,
    keep_workspace: bool = False,
    quiet: bool = False,
    verbose: bool = False,
) -> dict[str, Any]:
    scenario_path = scenario_path.resolve()
    variant_path = variant_path.resolve()
    scenario = load_json(scenario_path)
    variant = load_json(variant_path)
    scenario_dir = scenario_path.parent

    scenario_name = scenario.get("name", "<invalid-scenario>") if isinstance(scenario, dict) else "<invalid-scenario>"
    variant_name = variant.get("name", "<invalid-variant>") if isinstance(variant, dict) else "<invalid-variant>"
    result: dict[str, Any] = {
        "scenario": scenario_name,
        "variant": variant_name,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "success": False,
        "setup": [],
        "run": None,
        "evaluations": [],
        "usage": None,
    }
    temp_dir: Path | None = None
    workspace: Path | None = None
    workspace_fd: int | None = None
    started = time.monotonic()
    try:
        # Validate scenario-owned configuration before materializing fixtures or
        # running any setup/agent command. This is distinct from fixture I/O.
        try:
            _validate_scenario(scenario, scenario_dir)
            fixture_config = scenario["fixture"]
            task_source = scenario_dir / Path(scenario["task"])
            timeout = scenario.get("timeout_seconds", 900)
            configured_provenance = None
            if isinstance(fixture_config, dict):
                url, revision = _external_fixture_config(fixture_config)
                configured_provenance = {"url": url, "commit": revision}
                result["fixture_provenance"] = configured_provenance
        except (KeyError, TypeError, ValueError) as error:
            result["failure_reason"] = "scenario_configuration_failed"
            result["scenario_error"] = str(error)
            return result

        try:
            fixture, provenance = fixture_source(scenario_dir, fixture_config)
            temp_dir = Path(tempfile.mkdtemp(prefix=f"ai-tools-benchmark-{scenario['name']}-"))
            workspace = temp_dir / "workspace"
            _validate_fixture_links(fixture)
            # Preserve repository-internal links, but never dereference a link
            # into the host checkout while copying into an agent workspace.
            shutil.copytree(fixture, workspace, symlinks=True, ignore=shutil.ignore_patterns(".git"))
            task_path = temp_dir / "task.md"
            shutil.copy2(task_source, task_path)
            init_workspace_repo(workspace)
            workspace_fd = os.open(workspace, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
            if provenance is not None:
                result["fixture_provenance"] = provenance
        except Exception as error:
            result["failure_reason"] = "fixture_setup_failed"
            result["fixture_error"] = str(error)
            return result

        assert workspace is not None and temp_dir is not None
        env = os.environ.copy()
        env["PWD"] = str(workspace)
        env.update({str(k): str(v) for k, v in variant.get("env", {}).items()})
        setup_steps, setup_passed = run_setup(variant, task_path, workspace, env, timeout, quiet, verbose)
        result["setup"] = setup_steps
        if not setup_passed:
            result["failure_reason"] = "setup_failed"
            return result

        run_step = run_command(
            render_command(variant["command"], task_path, workspace),
            workspace,
            env,
            timeout,
            quiet,
            verbose,
        )
        result["run"] = run_step
        result["usage"] = collect_usage(variant, workspace)
        result["token_qualification"] = token_qualification(scenario, result["usage"])
        result["qualification"] = result["token_qualification"]

        try:
            inject_after_run(scenario_dir, workspace, scenario.get("inject_after_run", []), workspace_fd)
        except (OSError, ValueError, shutil.Error) as error:
            result["failure_reason"] = "injection_failed"
            result["injection_error"] = str(error)
            return result
        evaluation_steps, evaluations_passed = run_verifications(
            scenario, task_path, workspace, env, timeout, quiet, verbose
        )
        result["evaluations"] = evaluation_steps

        result["success"] = step_passed(run_step) and evaluations_passed
        if not result["success"]:
            result["failure_reason"] = "run_or_verification_failed"
        return result
    finally:
        if workspace_fd is not None:
            os.close(workspace_fd)
        result[DURATION_SECONDS] = round(time.monotonic() - started, 3)
        if keep_workspace and workspace is not None:
            result["workspace"] = str(workspace)
        elif temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)


def save_result(result: dict[str, Any], results_dir: Path | None = None) -> Path:
    global RESULT_COUNTER
    destination = results_dir or RESULTS_DIR
    destination.mkdir(parents=True, exist_ok=True)
    RESULT_COUNTER += 1
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    path = destination / f"{timestamp}-{RESULT_COUNTER}-{result['scenario']}-{result['variant']}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
    return path


def result_summary(result: dict[str, Any]) -> str:
    status = "PASS" if result["success"] else "FAIL"
    return f"{status} {result['scenario']} / {result['variant']} ({result[DURATION_SECONDS]}s)"


def command_run(args: argparse.Namespace) -> int:
    scenario_paths = []
    for value in args.scenarios[:-1]:
        path = Path(value)
        scenario_paths.append(path / "scenario.json" if path.is_dir() else path)
    variant = Path(args.scenarios[-1])
    exit_code = 0
    total = len(scenario_paths) * args.repeat
    execution = 0
    for scenario in scenario_paths:
        for repeat_index in range(1, args.repeat + 1):
            execution += 1
            scenario_data = load_json(scenario)
            print(
                f"[{execution}/{total}] {scenario_data['name']} / {load_json(variant)['name']} "
                f"(repeat {repeat_index}/{args.repeat}, timeout {int(scenario_data.get('timeout_seconds', 900))}s)"
            )
            result = execute_scenario(
                scenario,
                variant,
                keep_workspace=args.keep_workspace,
                quiet=args.quiet,
                verbose=args.verbose,
            )
            path = save_result(result, Path(args.results_dir) if args.results_dir else None)
            print(f"{result_summary(result)} -> {path}")
            if not result["success"]:
                exit_code = 1
    return exit_code


def command_compare(args: argparse.Namespace) -> int:
    results = [load_json(Path(path)) for path in args.results]
    groups: dict[str, list[dict[str, Any]]] = {}
    since = getattr(args, "since", None)
    for result in results:
        if since is not None and parse_timestamp(result["started_at"]) < since:
            continue
        if args.scenario and result.get("scenario") != args.scenario:
            continue
        if args.variant and result.get("variant") != args.variant:
            continue
        groups.setdefault((result["scenario"], result["variant"]), []).append(result)

    print("| Scenario | Variant | Runs | Success rate | Median time (s) | Median input tokens | Qualifying runs |")
    print("|---|---|---:|---:|---:|---:|---:|")
    for (scenario, variant), items in sorted(groups.items()):
        successes = sum(1 for item in items if item.get("success"))
        durations = [float(item[DURATION_SECONDS]) for item in items]
        input_tokens = [
            int(item["usage"][INPUT_TOKENS])
            for item in items
            if item.get("usage") and INPUT_TOKENS in item["usage"]
        ]
        median_tokens = str(int(statistics.median(input_tokens))) if input_tokens else "n/a"
        qualifying = sum(
            1
            for item in items
            if isinstance(item.get("token_qualification") or item.get("qualification"), dict)
            and (item.get("token_qualification") or item.get("qualification")).get("met") is True
        )
        print(
            f"| {scenario} | {variant} | {len(items)} | {successes / len(items):.0%} | "
            f"{statistics.median(durations):.2f} | {median_tokens} | {qualifying} |"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark coding agents, harnesses, models, and skills.")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    run_parser = subparsers.add_parser("run", help="Run one or more scenarios with one variant.")
    run_parser.add_argument("scenarios", nargs="+", help="Scenario paths followed by a variant path")
    run_parser.add_argument("--repeat", type=int, default=1)
    run_parser.add_argument("--keep-workspace", action="store_true")
    run_parser.add_argument("--results-dir")
    run_parser.add_argument("--verbose", action="store_true")
    run_parser.add_argument("--quiet", action="store_true")
    run_parser.set_defaults(func=command_run)

    compare_parser = subparsers.add_parser("compare", help="Compare saved result JSON files.")
    compare_parser.add_argument("results", nargs="+")
    compare_parser.add_argument("--scenario")
    compare_parser.add_argument("--variant")
    compare_parser.add_argument("--since", type=parse_timestamp)
    compare_parser.set_defaults(func=command_compare)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.subcommand == "run" and len(args.scenarios) < 2:
        parser.error("run requires at least one scenario and one variant")
    if getattr(args, "repeat", 1) < 1:
        parser.error("--repeat must be at least 1")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
