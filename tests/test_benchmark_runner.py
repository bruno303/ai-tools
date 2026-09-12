import argparse
import json
import contextlib
import io
import os
import shutil
import sys
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import benchmark
import opencode_usage


class BenchmarkRunnerTests(unittest.TestCase):
    def test_opencode_usage_aggregates_known_model_events_and_ignores_unknown(self):
        usage = opencode_usage.parse_usage([
            {"type": "step_finish", "part": {"type": "step-finish", "tokens": {"input": 10, "output": 4, "cache": {"read": 6}}, "cost": 0.25}},
            {"type": "tool_use", "part": {"type": "tool", "tool": "task", "new_field": True}},
            {"type": "future-event", "part": {"tokens": {"input": 999}, "cost": 99}},
            {"type": "step-finish-extra", "part": {"tokens": {"input": 999}, "cost": 99}},
        ])
        self.assertEqual(usage["input_tokens"], 10)
        self.assertEqual(usage["cached_input_tokens"], 6)
        self.assertEqual(usage["output_tokens"], 4)
        self.assertEqual(usage["model_calls"], 1)
        self.assertEqual(usage["subagent_calls"], 1)
        self.assertEqual(usage["cost"], 0.25)

    def test_opencode_wrapper_preserves_failure_and_writes_usage_atomically(self):
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, "-c", "import json; print(json.dumps({'type':'step_finish','part':{'type':'step-finish','tokens':{'input':2}}})); raise SystemExit(7)"]
            with contextlib.chdir(directory):
                self.assertEqual(opencode_usage.main(["--", *command]), 7)
                self.assertEqual(json.loads(Path(".benchmark-usage.json").read_text())["input_tokens"], 2)

    def test_opencode_wrapper_accepts_nested_usage_path(self):
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, "-c", "import json; print(json.dumps({'type':'step_finish','part':{'tokens':{'input':2}}}))"]
            with contextlib.chdir(directory):
                self.assertEqual(opencode_usage.main(["--usage-file", "nested/usage.json", "--", *command]), 0)
                self.assertEqual(json.loads(Path("nested/usage.json").read_text())["input_tokens"], 2)

    def test_opencode_wrapper_rejects_usage_paths_outside_workspace(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            outside_path = Path(outside) / "usage.json"
            link = Path(directory) / "link"
            link.symlink_to(outside, target_is_directory=True)
            for usage_file in ("nested/../usage.json", str(outside_path), "link/usage.json"):
                with self.subTest(usage_file=usage_file), contextlib.chdir(directory):
                    with self.assertRaises(SystemExit) as raised:
                        opencode_usage.main(["--usage-file", usage_file, "--", sys.executable, "-c", "pass"])
                    self.assertEqual(raised.exception.code, 2)
            self.assertFalse(outside_path.exists())

    def test_opencode_wrapper_rejects_directory_symlink_created_by_subprocess(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            nested = root / "nested"
            nested.mkdir()
            outside_path = Path(outside) / "usage.json"
            code = (
                "from pathlib import Path; "
                f"p=Path(r'{nested}'); p.rmdir(); p.symlink_to(r'{outside}', target_is_directory=True)"
            )
            command = [sys.executable, "-c", code]
            with contextlib.chdir(directory):
                with self.assertRaises((OSError, ValueError)):
                    opencode_usage.main(["--usage-file", "nested/usage.json", "--", *command])
            self.assertFalse(outside_path.exists())

    def test_opencode_wrapper_keeps_root_fd_when_subprocess_replaces_cwd(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            moved_root = root.with_name(root.name + "-moved")
            outside_path = Path(outside) / ".benchmark-usage.json"
            validated = root / "validated"
            code = (
                "from pathlib import Path\n"
                "import time\n"
                f"marker = Path(r'{validated}')\n"
                "while not marker.exists():\n"
                "    time.sleep(0.001)\n"
                f"p = Path(r'{root}')\n"
                f"p.rename(r'{moved_root}')\n"
                f"p.symlink_to(r'{outside}', target_is_directory=True)\n"
            )
            command = [sys.executable, "-c", code]
            original_validate = opencode_usage._validate_usage_path

            def validate_and_signal(value, allowed_directory=None):
                result = original_validate(value, allowed_directory)
                validated.touch()
                return result

            with contextlib.chdir(directory), unittest.mock.patch.object(
                opencode_usage, "_validate_usage_path", validate_and_signal
            ):
                self.assertEqual(opencode_usage.main(["--", *command]), 0)
            self.assertFalse(outside_path.exists())
            self.assertTrue((moved_root / ".benchmark-usage.json").exists())

    def test_rendered_opencode_variant_runs_from_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scenario = self.make_scenario(root, "rendered", [])
            variant = ROOT / "benchmarks" / "variants" / "opencode.example.json"
            workspace = root / "workspace"
            workspace.mkdir()
            task = root / "task.md"
            task.write_text("task", encoding="utf-8")
            command = benchmark.render_command(benchmark.load_json(variant)["command"], task, workspace)
            self.assertEqual(Path(command[1]), ROOT / "benchmarks" / "opencode_usage.py")
            separator = command.index("--")
            command[separator + 1:] = [sys.executable, "-c", "import json; print(json.dumps({'type':'step_finish','part':{'type':'step-finish','tokens':{'input':3}}}))"]
            completed = benchmark.run_command(command, workspace, os.environ.copy(), 10, quiet=True)
            self.assertEqual(completed["exit_code"], 0)
            self.assertEqual(json.loads((workspace / ".benchmark-usage.json").read_text())["input_tokens"], 3)
    def make_scenario(self, root, name, command, verification=None, hidden=False):
        scenario_dir = root / name
        fixture = scenario_dir / "fixture"
        fixture.mkdir(parents=True)
        (fixture / "tracked.txt").write_text("original", encoding="utf-8")
        (scenario_dir / "task.md").write_text("task", encoding="utf-8")
        if hidden:
            (scenario_dir / "hidden.txt").write_text("hidden", encoding="utf-8")
        scenario = {
            "name": name,
            "fixture": "fixture",
            "task": "task.md",
            "timeout_seconds": 10,
            "verification": verification or [],
        }
        if hidden:
            scenario["inject_after_run"] = [{"source": "hidden.txt", "destination": "hidden.txt"}]
        path = scenario_dir / "scenario.json"
        path.write_text(json.dumps(scenario), encoding="utf-8")
        return path

    def make_variant(self, root, name, command):
        path = root / f"{name}.json"
        path.write_text(json.dumps({"name": name, "command": command}), encoding="utf-8")
        return path

    def test_workspace_is_isolated_git_repo_with_correct_pwd(self):
        if shutil.which("git") is None:
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code = (
                "import os, subprocess, sys; "
                "from pathlib import Path; "
                f"assert os.environ['PWD'] == r'{{workspace}}', os.environ['PWD']; "
                "assert os.getcwd() == r'{workspace}', os.getcwd(); "
                "head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True); "
                "assert head.returncode == 0, head.stderr; "
                "status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True); "
                "assert status.returncode == 0, status.stderr; "
                f"assert status.stdout.strip() == '', status.stdout; "
                "assert Path('tracked.txt').read_text() == 'original'"
            )
            scenario = self.make_scenario(root, "git-workspace", [])
            variant = self.make_variant(root, "git-check", [sys.executable, "-c", code])
            result = benchmark.execute_scenario(scenario, variant)

            self.assertTrue(result["success"], result.get("failure_reason"))
            self.assertEqual((scenario.parent / "fixture" / "tracked.txt").read_text(), "original")

    def test_destructive_variant_does_not_modify_fixture_and_workspace_is_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace_path = root / "workspace-path.txt"
            code = (
                "from pathlib import Path; "
                f"w=Path(r'{workspace_path}'); w.write_text(r'{{workspace}}'); "
                "p=Path(r'{workspace}')/'tracked.txt'; p.write_text('changed'); "
                "(Path(r'{workspace}')/'created.txt').write_text('created')"
            )
            scenario = self.make_scenario(root, "isolated", [])
            variant = self.make_variant(root, "destructive", [sys.executable, "-c", code])
            result = benchmark.execute_scenario(scenario, variant)

            self.assertTrue(result["success"])
            self.assertEqual((scenario.parent / "fixture" / "tracked.txt").read_text(), "original")
            self.assertFalse(Path(workspace_path.read_text()).exists())

    def test_batch_results_are_unique_and_capture_hidden_test_timing(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as results:
            root = Path(directory)
            verification = [
                {
                    "name": "hidden",
                    "command": [sys.executable, "-c", "from pathlib import Path; assert Path('hidden.txt').exists()"],
                }
            ]
            first = self.make_scenario(root, "first", [], verification, hidden=True)
            second = self.make_scenario(root, "second", [], verification, hidden=True)
            code = "from pathlib import Path; assert not Path('hidden.txt').exists()"
            variant = self.make_variant(root, "fast", [sys.executable, "-c", code])

            args = type("Args", (), {
                "scenarios": [str(first), str(second), str(variant)],
                "repeat": 2,
                "keep_workspace": False,
                "results_dir": results,
                "verbose": False,
                "quiet": True,
            })()
            self.assertEqual(benchmark.command_run(args), 0)
            paths = sorted(Path(results).glob("*.json"))
            self.assertEqual(len(paths), 4)
            self.assertEqual(len({path.name for path in paths}), 4)
            for path in paths:
                result = json.loads(path.read_text(encoding="utf-8"))
                self.assertTrue(result["success"])
                self.assertIn(result["scenario"], {"first", "second"})
                self.assertEqual(result["variant"], "fast")
                self.assertIsNotNone(result["run"])
                self.assertEqual(len(result["evaluations"]), 1)
                self.assertIn("setup", result)
                self.assertIn("duration_seconds", result)

    def test_failure_result_has_failure_reason(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as results:
            root = Path(directory)
            scenario = self.make_scenario(root, "failure", [])
            variant = self.make_variant(root, "bad", [sys.executable, "-c", "raise SystemExit(3)"])
            args = type("Args", (), {
                "scenarios": [str(scenario), str(variant)],
                "repeat": 1,
                "keep_workspace": False,
                "results_dir": results,
                "verbose": False,
                "quiet": True,
            })()
            self.assertEqual(benchmark.command_run(args), 1)
            result = json.loads(next(Path(results).glob("*.json")).read_text(encoding="utf-8"))
            self.assertFalse(result["success"])
            self.assertEqual(result["failure_reason"], "run_or_verification_failed")

    def test_leader_exit_does_not_wait_for_child_pipe_inheritor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child_pid_path = root / "child.pid"
            child_code = "import time; time.sleep(30)"
            code = (
                "import subprocess; from pathlib import Path; "
                f"child=subprocess.Popen([{sys.executable!r}, '-c', {child_code!r}]); "
                f"Path(r'{child_pid_path}').write_text(str(child.pid)); "
                "print('parent complete', flush=True)"
            )
            scenario = self.make_scenario(root, "pipe-inheritor", [])
            variant = self.make_variant(root, "leader-exits", [sys.executable, "-c", code])

            started = time.monotonic()
            result = benchmark.execute_scenario(scenario, variant)
            elapsed = time.monotonic() - started

            self.assertTrue(result["success"])
            self.assertEqual(result["run"]["exit_code"], 0)
            self.assertFalse(result["run"]["timed_out"])
            self.assertLess(elapsed, 5)
            self.assertIn("parent complete", result["run"]["stdout"])

            child_pid = int(child_pid_path.read_text(encoding="utf-8"))
            for _ in range(20):
                try:
                    os.kill(child_pid, 0)
                except ProcessLookupError:
                    break
                time.sleep(0.05)
            else:
                self.fail("inherited-pipe child was not terminated")

    def test_compare_since_is_inclusive_and_handles_timezones(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results = []
            for name, started_at in (
                ("before", "2024-01-01T11:59:59+00:00"),
                ("at", "2024-01-01T12:00:00+00:00"),
                ("offset", "2024-01-01T13:00:00+01:00"),
            ):
                path = root / f"{name}.json"
                path.write_text(
                    json.dumps(
                        {
                            "scenario": "scenario",
                            "variant": name,
                            "started_at": started_at,
                            "success": True,
                            "duration_seconds": 1,
                        }
                    ),
                    encoding="utf-8",
                )
                results.append(str(path))

            args = type("Args", (), {
                "results": results,
                "scenario": None,
                "variant": None,
                "since": benchmark.parse_timestamp("2024-01-01T12:00:00-00:00"),
            })()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(benchmark.command_compare(args), 0)
            self.assertIn("| scenario | at | 1 |", output.getvalue())
            self.assertIn("| scenario | offset | 1 |", output.getvalue())
            self.assertNotIn("| scenario | before |", output.getvalue())

    def test_compare_since_composes_with_scenario_and_variant_filters(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for index, (scenario, variant) in enumerate((("keep", "target"), ("keep", "other"), ("skip", "target"))):
                path = root / f"{index}.json"
                path.write_text(json.dumps({
                    "scenario": scenario,
                    "variant": variant,
                    "started_at": "2024-01-02T00:00:00Z",
                    "success": True,
                    "duration_seconds": 1,
                }), encoding="utf-8")
                paths.append(str(path))
            args = type("Args", (), {
                "results": paths,
                "scenario": "keep",
                "variant": "target",
                "since": benchmark.parse_timestamp("2024-01-01T00:00:00Z"),
            })()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                benchmark.command_compare(args)
            self.assertIn("| keep | target | 1 |", output.getvalue())
            self.assertNotIn("other", output.getvalue())
            self.assertNotIn("skip", output.getvalue())

    def test_compare_since_rejects_invalid_timestamp(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            benchmark.parse_timestamp("not-a-timestamp")


if __name__ == "__main__":
    unittest.main()
