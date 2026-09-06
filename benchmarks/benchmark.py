#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import statistics
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
Command = str | list[str]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_command(command: Command) -> list[str]:
    if isinstance(command, str):
        return shlex.split(command)
    return [str(part) for part in command]


def render_command(command: Command, task_path: Path, workspace: Path) -> list[str]:
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


def run_command(command: list[str], cwd: Path, env: dict[str, str], timeout: int | None) -> dict[str, Any]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": command,
            "exit_code": completed.returncode,
            "duration_seconds": round(time.monotonic() - started, 3),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "exit_code": None,
            "duration_seconds": round(time.monotonic() - started, 3),
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
        }


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


def execute_scenario(scenario_path: Path, variant_path: Path, keep_workspace: bool = False) -> dict[str, Any]:
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

    env = os.environ.copy()
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
        for command in variant.get("setup", []):
            step = run_command(render_command(command, task_path, workspace), workspace, env, timeout)
            result["setup"].append(step)
            if step["exit_code"] != 0:
                result["failure_reason"] = "setup_failed"
                return result

        run_step = run_command(render_command(variant["command"], task_path, workspace), workspace, env, timeout)
        result["run"] = run_step
        result["usage"] = collect_usage(variant, workspace)

        inject_after_run(scenario_dir, workspace, scenario.get("inject_after_run", []))

        all_passed = run_step["exit_code"] == 0 and not run_step["timed_out"]
        for evaluation in scenario.get("verification", []):
            command = render_command(evaluation["command"], task_path, workspace)
            step = run_command(command, workspace, env, int(evaluation.get("timeout_seconds", timeout)))
            step["name"] = evaluation["name"]
            step["passed"] = step["exit_code"] == 0 and not step["timed_out"]
            result["evaluations"].append(step)
            all_passed = all_passed and step["passed"]

        result["success"] = all_passed
        if not all_passed:
            result["failure_reason"] = "run_or_verification_failed"
        return result
    finally:
        result["duration_seconds"] = round(time.monotonic() - started, 3)
        if keep_workspace:
            result["workspace"] = str(workspace)
        else:
            shutil.rmtree(temp_dir, ignore_errors=True)


def save_result(result: dict[str, Any]) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RESULTS_DIR / f"{timestamp}-{result['scenario']}-{result['variant']}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
    return path


def result_summary(result: dict[str, Any]) -> str:
    status = "PASS" if result["success"] else "FAIL"
    return f"{status} {result['scenario']} / {result['variant']} ({result['duration_seconds']}s)"


def command_run(args: argparse.Namespace) -> int:
    scenario = Path(args.scenario)
    variant = Path(args.variant)
    exit_code = 0
    for _ in range(args.repeat):
        result = execute_scenario(scenario, variant, keep_workspace=args.keep_workspace)
        path = save_result(result)
        print(f"{result_summary(result)} -> {path}")
        if not result["success"]:
            exit_code = 1
    return exit_code


def command_compare(args: argparse.Namespace) -> int:
    results = [load_json(Path(path)) for path in args.results]
    groups: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        groups.setdefault(result["variant"], []).append(result)

    print("| Variant | Runs | Success rate | Median time (s) | Median input tokens |")
    print("|---|---:|---:|---:|---:|")
    for variant, items in sorted(groups.items()):
        successes = sum(1 for item in items if item.get("success"))
        durations = [float(item["duration_seconds"]) for item in items]
        input_tokens = [
            int(item["usage"]["input_tokens"])
            for item in items
            if item.get("usage") and "input_tokens" in item["usage"]
        ]
        median_tokens = str(int(statistics.median(input_tokens))) if input_tokens else "n/a"
        print(
            f"| {variant} | {len(items)} | {successes / len(items):.0%} | "
            f"{statistics.median(durations):.2f} | {median_tokens} |"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark coding agents, harnesses, models, and skills.")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    run_parser = subparsers.add_parser("run", help="Run a scenario with one variant.")
    run_parser.add_argument("scenario", help="Path to scenario.json")
    run_parser.add_argument("variant", help="Path to variant.json")
    run_parser.add_argument("--repeat", type=int, default=1)
    run_parser.add_argument("--keep-workspace", action="store_true")
    run_parser.set_defaults(func=command_run)

    compare_parser = subparsers.add_parser("compare", help="Compare saved result JSON files.")
    compare_parser.add_argument("results", nargs="+")
    compare_parser.set_defaults(func=command_compare)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if getattr(args, "repeat", 1) < 1:
        parser.error("--repeat must be at least 1")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
