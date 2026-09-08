import importlib.util
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "install-agents.sh"
OPENCODE_INSTALLER = ROOT / "opencode" / "install.sh"
VALIDATOR = ROOT / "scripts" / "validate-agent-definitions.py"

validator_spec = importlib.util.spec_from_file_location("validate_agent_definitions", VALIDATOR)
assert validator_spec is not None
assert validator_spec.loader is not None
validator_module = importlib.util.module_from_spec(validator_spec)
validator_spec.loader.exec_module(validator_module)


class AgentSetupTests(unittest.TestCase):
    def run_installer(self, *args, env=None):
        return subprocess.run([str(INSTALLER), *args], cwd=ROOT, text=True, capture_output=True, env=env)

    def test_validator_succeeds(self):
        result = subprocess.run(["python3", str(VALIDATOR)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_frontmatter_parser_preserves_nested_and_scalar_values(self):
        text = """---
root:
  child: "value"
  apostrophe: 'it''s'
empty:
---
"""

        parsed = validator_module.parse_frontmatter(text)

        self.assertEqual(
            parsed,
            {"root": {"child": "value", "apostrophe": "it's"}, "empty": {}},
        )

    def test_frontmatter_parser_rejects_non_mapping_entries(self):
        with self.assertRaisesRegex(ValueError, "expected a mapping entry"):
            validator_module.parse_frontmatter("---\nnot a mapping\n---\n")

    def test_active_profiles_only_define_harness_metadata_and_models(self):
        expected = {
            "opencode": {"executor.md", "reviewer.md"},
            "codex": {"executor.toml", "reviewer.toml"},
            "claude": {"executor.md", "reviewer.md"},
        }
        for harness, filenames in expected.items():
            with self.subTest(harness=harness):
                for filename in filenames:
                    path = ROOT / harness / "agents" / filename
                    if path.suffix == ".toml":
                        definition = tomllib.loads(path.read_text(encoding="utf-8"))
                        self.assertEqual(
                            set(definition),
                            {"name", "description", "model", "model_reasoning_effort", "developer_instructions"},
                        )
                        self.assertEqual(definition["developer_instructions"], "")
                    else:
                        definition = validator_module.parse_frontmatter(path.read_text(encoding="utf-8"))
                        self.assertEqual(
                            set(definition),
                            {"mode", "model", "reasoningEffort"} if harness == "opencode" else {"name", "description", "model"},
                        )

    def test_installs_each_harness_destination(self):
        destinations = {"opencode": "agents", "codex": ".codex/agents", "claude": ".claude/agents"}
        for harness, relative in destinations.items():
            with self.subTest(harness=harness), tempfile.TemporaryDirectory() as target:
                result = self.run_installer(harness, target)
                self.assertEqual(result.returncode, 0, result.stderr)
                destination = Path(target) / relative
                self.assertEqual({path.name for path in destination.iterdir()}, {"executor.md", "reviewer.md"} if harness != "codex" else {"executor.toml", "reviewer.toml"})

    def test_rejects_invalid_harness_and_missing_target(self):
        invalid = self.run_installer("unknown", "/tmp/agent-test-target")
        missing = self.run_installer("opencode")
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("Unknown harness", invalid.stderr)
        self.assertNotEqual(missing.returncode, 0)

    def test_clean_scopes_to_selected_harness(self):
        with tempfile.TemporaryDirectory() as target:
            self.assertEqual(self.run_installer("opencode", target).returncode, 0)
            self.assertEqual(self.run_installer("codex", target).returncode, 0)
            extra = Path(target) / "agents" / "keep.txt"
            extra.write_text("keep", encoding="utf-8")
            result = self.run_installer("--clean", "opencode", target)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(extra.exists())
            self.assertTrue((Path(target) / ".codex/agents/executor.toml").exists())

    def test_clean_rejects_destination_overlapping_install_source(self):
        with tempfile.TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)
            fixture_installer = workspace_path / "install-agents.sh"
            shutil.copy2(INSTALLER, fixture_installer)
            fixture_installer.chmod(0o755)
            shutil.copytree(ROOT / "opencode", workspace_path / "opencode")
            source_dir = workspace_path / "opencode" / "agents"
            before = {path.name: path.read_text(encoding="utf-8") for path in source_dir.iterdir()}

            result = subprocess.run(
                [str(fixture_installer), "--clean", "opencode", str(workspace_path / "opencode")],
                cwd=workspace_path,
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("overlapping install source", result.stderr)
            after = {path.name: path.read_text(encoding="utf-8") for path in source_dir.iterdir()}
            self.assertEqual(after, before)

    def test_archived_legacy_definitions_are_not_installed(self):
        with tempfile.TemporaryDirectory() as target:
            result = self.run_installer("opencode", target)
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = {path.name for path in (Path(target) / "agents").iterdir()}
            self.assertNotIn("architect.md", installed)
            self.assertNotIn("builder.md", installed)
            self.assertNotIn("spec-driver.md", installed)

    def test_opencode_wrapper_delegates_and_removes_models(self):
        with tempfile.TemporaryDirectory() as target:
            target_path = Path(target)
            self.assertEqual(self.run_installer("codex", target).returncode, 0)
            unrelated = target_path / ".codex" / "agents" / "keep.toml"
            unrelated.write_text("keep", encoding="utf-8")

            result = subprocess.run(
                [str(OPENCODE_INSTALLER), "--clean", "--remove-model", target],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            destination = target_path / "agents"
            self.assertEqual({path.name for path in destination.iterdir()}, {"executor.md", "reviewer.md"})
            for agent in ("executor.md", "reviewer.md"):
                self.assertNotIn("model:", (destination / agent).read_text(encoding="utf-8"))
            self.assertTrue(unrelated.exists())

    def test_validator_rejects_malformed_codex_toml_without_touching_repository(self):
        with tempfile.TemporaryDirectory() as root:
            fixture_root = Path(root)
            shutil.copytree(ROOT / "codex", fixture_root / "codex")
            executor = fixture_root / "codex" / "agents" / "executor.toml"
            executor.write_text(
                executor.read_text(encoding="utf-8") + "\nbroken =\n",
                encoding="utf-8",
            )

            errors = validator_module.validate_harness(fixture_root, "codex")

            self.assertTrue(any("malformed toml configuration" in error for error in errors), errors)

    def test_validator_rejects_malformed_frontmatter_without_touching_repository(self):
        with tempfile.TemporaryDirectory() as root:
            fixture_root = Path(root)
            shutil.copytree(ROOT / "opencode", fixture_root / "opencode")
            executor = fixture_root / "opencode" / "agents" / "executor.md"
            executor.write_text(
                """---
mode: subagent
model: opencode/gpt-5.6-luna
reasoningEffort: medium
---
unexpected instruction
""",
                encoding="utf-8",
            )

            errors = validator_module.validate_harness(fixture_root, "opencode")

            self.assertTrue(any("malformed frontmatter configuration" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
