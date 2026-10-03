import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "subagent-plan-execution" / "SKILL.md"
PLAN_SKILL = ROOT / "skills" / "plan-implementation" / "SKILL.md"
CODE_REVIEW_SKILL = ROOT / "skills" / "code-review" / "SKILL.md"
REVIEWER_PROMPT = ROOT / "skills" / "subagent-plan-execution" / "references" / "reviewer_prompt.md"
FINAL_REVIEWER_PROMPT = ROOT / "skills" / "subagent-plan-execution" / "references" / "final_reviewer_prompt.md"


class SubagentPlanExecutionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_text = SKILL.read_text(encoding="utf-8")
        cls.normalized_skill_text = re.sub(r"\s+", " ", cls.skill_text)
        cls.plan_skill_text = PLAN_SKILL.read_text(encoding="utf-8")
        cls.normalized_plan_skill_text = re.sub(r"\s+", " ", cls.plan_skill_text)
        cls.code_review_text = CODE_REVIEW_SKILL.read_text(encoding="utf-8")
        cls.normalized_code_review_text = re.sub(r"\s+", " ", cls.code_review_text)
        cls.reviewer_prompt_text = REVIEWER_PROMPT.read_text(encoding="utf-8")
        cls.normalized_reviewer_prompt_text = re.sub(r"\s+", " ", cls.reviewer_prompt_text)
        cls.final_reviewer_prompt_text = FINAL_REVIEWER_PROMPT.read_text(encoding="utf-8")
        cls.normalized_final_reviewer_prompt_text = re.sub(
            r"\s+", " ", cls.final_reviewer_prompt_text
        )

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

    def test_worker_briefs_preserve_the_confirmed_plan_contract(self):
        for phrase in (
            "confirmed requirements, constraints, non-goals, and important decisions",
            "negative constraints",
            "acceptance evidence",
            "test-placement conventions",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.normalized_plan_skill_text)

        for phrase in (
            "confirmed requirements, constraints, non-goals, and important decisions",
            "negative constraints and defaults that affect behavior",
            "acceptance evidence",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.normalized_skill_text)

    def test_expected_output_paths_are_validated_before_dispatch(self):
        for phrase in (
            "validate every expected output path against the repository",
            "exists at the exact declared location",
            "a prerequisite task declares it as created",
            "exists or is declared by a prerequisite",
            "Check each task's paths again in Step 1a",
            "test-placement conventions",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.normalized_skill_text)

    def test_plan_format_has_a_home_for_constraints_and_briefs_carry_them(self):
        self.assertIn("## Constraints and acceptance evidence", self.skill_text)
        for phrase in (
            "add a constraints block",
            "The dependency set and expected-output scope follow the constraints block",
            "A constraint is applicable to a brief when it is global or names that task's paths or behavior",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.normalized_skill_text)
        self.assertIn("a path an earlier task in the plan creates", self.normalized_plan_skill_text)

    def test_review_status_is_a_strict_protocol_not_an_inferred_pass(self):
        self.assertIn(
            "A missing, malformed, or different status is a protocol failure",
            self.normalized_skill_text,
        )
        self.assertIn("Do not infer a pass", self.normalized_skill_text)

        for prompt_text in (
            self.normalized_reviewer_prompt_text,
            self.normalized_final_reviewer_prompt_text,
        ):
            self.assertIn("Use only those two status values", prompt_text)
            self.assertIn("protocol failure", prompt_text)
            self.assertIn("never report or infer a pass", prompt_text)

    def test_malformed_verdict_retry_differs_between_task_and_final_review(self):
        task_section = self.normalized_skill_text.split("#### Reviewer result handling")[1]
        task_section = task_section.split("## Step 2")[0]
        final_section = self.normalized_skill_text.split("## Step 2")[1].split("## Step 3")[0]

        self.assertIn("gets exactly one retry", task_section)
        self.assertIn("a malformed final-review verdict stops immediately and gets no retry", task_section)
        self.assertNotIn("gets exactly one retry", final_section)
        self.assertIn("a malformed final-review verdict gets no retry", final_section)
        self.assertIn("stop and report it immediately", final_section)

    def test_review_findings_require_evidence_and_a_baseline_check(self):
        for phrase in (
            "verify the baseline behavior",
            "unchanged pre-existing behavior",
            "Support every finding with concrete evidence",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.normalized_code_review_text)

        for prompt_text in (
            self.normalized_reviewer_prompt_text,
            self.normalized_final_reviewer_prompt_text,
        ):
            schema = prompt_text.split("FINDINGS: - severity:")[1].split("```")[0]
            self.assertIn("issue: ... evidence: ... fix: ...", schema)
            self.assertIn("baseline behavior", prompt_text)

    def test_progress_updates_are_limited_to_meaningful_events(self):
        self.assertIn(
            "meaningful discoveries, decisions, blockers, and completion",
            self.normalized_skill_text,
        )


if __name__ == "__main__":
    unittest.main()
