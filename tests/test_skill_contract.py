import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "subagent-plan-execution"


class SubagentPlanExecutionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    def test_workflow_roles_select_the_expected_profiles(self):
        expected_roles = {
            "Task implementer": "executor",
            "Task-scoped fixer": "executor",
            "Lightweight task reviewer": "reviewer",
            "Final aggregate reviewer": "reviewer",
            "Final consolidated fixer": "executor",
        }
        for role, profile in expected_roles.items():
            with self.subTest(role=role):
                self.assertRegex(
                    self.skill_text,
                    rf"\|\s*{re.escape(role)}\s*\|\s*`{profile}`\s*\|",
                )

    def test_skill_requires_profiles_without_hard_coding_models(self):
        self.assertIn("MISSING_AGENT_PROFILE", self.skill_text)
        self.assertIn("Do not silently fall back", self.skill_text)
        self.assertIn("`agent` or `agent_type`", self.skill_text)
        for model_identifier in ("gpt-5.6", "haiku", "sonnet", "opencode/"):
            with self.subTest(model_identifier=model_identifier):
                self.assertNotIn(model_identifier, self.skill_text)

    def test_referenced_prompt_templates_exist(self):
        references = re.findall(r"`references/([^`]+\.md)`", self.skill_text)
        self.assertTrue(references)
        for name in references:
            with self.subTest(template=name):
                self.assertTrue((SKILL_DIR / "references" / name).is_file())

    def test_reviewer_templates_expose_expected_handback_fields(self):
        for name in ("reviewer_prompt.md", "final_reviewer_prompt.md"):
            with self.subTest(template=name):
                text = (SKILL_DIR / "references" / name).read_text(encoding="utf-8")
                schema = re.search(r"```md\n(.*?)```", text, re.DOTALL)
                self.assertIsNotNone(schema)
                fields = schema.group(1)
                self.assertRegex(fields, r"STATUS:\s*PASSED\s*\|\s*CHANGES_REQUESTED")
                self.assertIn("FINDINGS:", fields)
                for field in ("severity", "file", "line", "issue", "evidence", "fix"):
                    self.assertRegex(fields, rf"(?m)^\s*(?:-\s*)?{field}:")


if __name__ == "__main__":
    unittest.main()
