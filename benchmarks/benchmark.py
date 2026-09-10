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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
DURATION_SECONDS = "duration_seconds"
INPUT_TOKENS = "input_tokens"
RESULT_COUNTER = 0


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_command(command: str | list[str]) -> list[str]:
    if isinstance(command, str):
        return shlex.split(command)
    return [str(part) for part in command]


def render_command(command: str | list[str], task_path: Path, workspace: Path) -> list[str]:
    task_content = task_path.read_text(encoding="utf-8")
    replacements = {
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
            if not quiet and not verbose and now >= next_heartbeat:
                heartbeat = f"running {int(now - started)}s / {timeout}s"
                if os.isatty(2):
                    print(f"\r{heartbeat}", end="", file=os.sys.stderr, flush=True)
                else:
                    print(heartbeat, file=os.sys.stderr, flush=True)
                next_heartbeat = now + 15
            events = selector.select(timeout=0.2)
            for key, _ in events:
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
    finally:
        terminate_process_group(process)
        drain_deadline = time.monotonic() + 1
        while selector.get_map() and time.monotonic() < drain_deadline:
            for key, _ in selector.select(timeout=0.05):
                data = os.read(key.fileobj.fileno(), 65536)
                if not data:
                    selector.unregister(key.fileobj)
                    continue
                output[key.data].extend(data)
                if verbose and not quiet:
                    text = data.decode(errors="replace")
                    for line in text.splitlines(True):
                        print(f"[{key.data}] {line}", end="", file=os.sys.stderr, flush=True)
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
            "GIT_AUTHOR_NAME": "benchmark",
            "GIT_AUTHOR_EMAIL": "benchmark@localhost",
            "GIT_COMMITTER_NAME": "benchmark",
            "GIT_COMMITTER_EMAIL": "benchmark@localhost",
        }
    )
    try:
        subprocess.run(["git", "init", "-q"], cwd=workspace, env=git_env, capture_output=True, timeout=30, check=False)
        subprocess.run(
            ["git", "config", "user.name", "benchmark"], cwd=workspace, env=git_env, capture_output=True, timeout=30, check=False
        )
        subprocess.run(
            ["git", "config", "user.email", "benchmark@localhost"], cwd=workspace, env=git_env, capture_output=True, timeout=30, check=False
        )
        subprocess.run(["git", "add", "-A"], cwd=workspace, env=git_env, capture_output=True, timeout=30, check=False)
        subprocess.run(
            ["git", "commit", "-q", "-m", "scenario fixture"], cwd=workspace, env=git_env, capture_output=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError):
        pass


def inject_after_run(scenario_dir: Path, workspace: Path, injections: list[dict[str, str]]) -> None:
    for injection in injections:
        source = scenario_dir / injection["source"]
        destination = workspace / injection["destination"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(source, destination)


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

    fixture = scenario_dir / scenario["fixture"]
    task_source = scenario_dir / scenario["task"]
    timeout = int(scenario.get("timeout_seconds", 900))

    temp_dir = Path(tempfile.mkdtemp(prefix=f"ai-tools-benchmark-{scenario['name']}-"))
    workspace = temp_dir / "workspace"
    shutil.copytree(fixture, workspace)
    task_path = temp_dir / "task.md"
    shutil.copy2(task_source, task_path)
    init_workspace_repo(workspace)

    env = os.environ.copy()
    env["PWD"] = str(workspace)
    env.update({str(k): str(v) for k, v in variant.get("env", {}).items()})

    result: dict[str, Any] = {
        "scenario": scenario["name"],
        "variant": variant["name"],
        "started_at": datetime.now(timezone.utc).isoformat(),
        "success": False,
        "setup": [],
        "run": None,
        "evaluations": [],
        "usage": None,
    }

    started = time.monotonic()
    try:
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

        inject_after_run(scenario_dir, workspace, scenario.get("inject_after_run", []))
        evaluation_steps, evaluations_passed = run_verifications(
            scenario, task_path, workspace, env, timeout, quiet, verbose
        )
        result["evaluations"] = evaluation_steps

        result["success"] = step_passed(run_step) and evaluations_passed
        if not result["success"]:
            result["failure_reason"] = "run_or_verification_failed"
        return result
    finally:
        result[DURATION_SECONDS] = round(time.monotonic() - started, 3)
        if keep_workspace:
            result["workspace"] = str(workspace)
        else:
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
    for result in results:
        if args.scenario and result.get("scenario") != args.scenario:
            continue
        if args.variant and result.get("variant") != args.variant:
            continue
        groups.setdefault((result["scenario"], result["variant"]), []).append(result)

    print("| Scenario | Variant | Runs | Success rate | Median time (s) | Median input tokens |")
    print("|---|---|---:|---:|---:|---:|")
    for (scenario, variant), items in sorted(groups.items()):
        successes = sum(1 for item in items if item.get("success"))
        durations = [float(item[DURATION_SECONDS]) for item in items]
        input_tokens = [
            int(item["usage"][INPUT_TOKENS])
            for item in items
            if item.get("usage") and INPUT_TOKENS in item["usage"]
        ]
        median_tokens = str(int(statistics.median(input_tokens))) if input_tokens else "n/a"
        print(
            f"| {scenario} | {variant} | {len(items)} | {successes / len(items):.0%} | "
            f"{statistics.median(durations):.2f} | {median_tokens} |"
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
