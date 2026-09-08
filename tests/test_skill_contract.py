import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "subagent-plan-execution" / "SKILL.md"


class SubagentPlanExecutionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_text = SKILL.read_text(encoding="utf-8")

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


if __name__ == "__main__":
    unittest.main()
