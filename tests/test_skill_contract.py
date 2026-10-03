import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "subagent-plan-execution" / "SKILL.md"
REVIEWER_PROMPT = ROOT / "skills" / "subagent-plan-execution" / "references" / "reviewer_prompt.md"
FINAL_REVIEWER_PROMPT = ROOT / "skills" / "subagent-plan-execution" / "references" / "final_reviewer_prompt.md"


class SubagentPlanExecutionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_text = SKILL.read_text(encoding="utf-8")
        cls.reviewer_prompt_text = REVIEWER_PROMPT.read_text(encoding="utf-8")
        cls.final_reviewer_prompt_text = FINAL_REVIEWER_PROMPT.read_text(encoding="utf-8")

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

    def test_lightweight_reviewer_defers_model_selection_to_its_profile(self):
        self.assertIn("reviewer profile controls model and reasoning settings", self.reviewer_prompt_text)
        self.assertNotIn("fast\nmodel with low or medium reasoning", self.reviewer_prompt_text)

    def test_task_review_uses_a_bounded_repair_rereview(self):
        self.assertIn("Use at most two lightweight review passes for a task", self.skill_text)
        self.assertIn("REVIEW_LOOP_EXHAUSTED", self.skill_text)
        self.assertIn("review_mode=repair", self.skill_text)
        self.assertNotIn("Do not re-review the task.", self.skill_text)

        self.assertIn("**Mode:** `{review_mode}`", self.reviewer_prompt_text)
        self.assertIn("**Previous findings:** `{previous_findings}`", self.reviewer_prompt_text)
        self.assertIn("do not repeat a finding merely to restate it", self.reviewer_prompt_text)

    def test_final_review_uses_a_bounded_repair_rereview(self):
        self.assertIn("Use at most two full aggregate review passes", self.skill_text)
        self.assertIn("FINAL_REVIEW_LOOP_EXHAUSTED", self.skill_text)
        self.assertIn("Passing the initial review must never trigger a redundant second review", self.skill_text)

        self.assertIn("**Mode:** `{review_mode}`", self.final_reviewer_prompt_text)
        self.assertIn("**Previous findings:** `{previous_findings}`", self.final_reviewer_prompt_text)
        self.assertIn("Only report still-unresolved findings", self.final_reviewer_prompt_text)


if __name__ == "__main__":
    unittest.main()
