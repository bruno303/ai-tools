import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "rfc-implementation-plan" / "SKILL.md"
EXAMPLES = ROOT / "skills" / "rfc-implementation-plan" / "references" / "examples.md"


class RfcImplementationPlanSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_text = SKILL.read_text(encoding="utf-8")
        cls.examples_text = EXAMPLES.read_text(encoding="utf-8")

    def test_skill_and_frontmatter_exist(self):
        self.assertTrue(SKILL.is_file())
        self.assertRegex(self.skill_text, r"\A---\s*\nname:\s*rfc-implementation-plan\s*\n")
        self.assertRegex(self.skill_text, r"description:\s*.+\n---")

    def test_trigger_and_scope_boundaries(self):
        for phrase in ("approved", "mostly final", "draft", "redesign", "subagent-plan-execution", "explicitly invoked"):
            self.assertIn(phrase, self.skill_text.lower())
        for phrase in ("must not implement", "run tests", "code review", "worktrees", "dispatch subagents"):
            self.assertIn(phrase, self.skill_text.lower())

    def test_required_guidance_and_output_contract(self):
        for phrase in (
            "explicit RFC decisions", "repository guidance", "current code and tests",
            "nearby patterns", "low-risk inference", "goals", "non-goals", "constraints",
            "selected design", "compatibility", "rollout", "acceptance criteria",
            "abstractions", "integration points", "migrations", "infrastructure",
            "operational", "RFC-settled", "repository-derived detail",
            "contradiction", "implementation-critical decision", "cohesive outcome",
            "parallel-safe", "task-level validation", "Final integration and validation",
            "Known files/artifacts", "exact-path allowlist", "pre-dispatch normalization",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.skill_text.lower())

        for section in ("Implementation summary", "Affected areas", "Assumptions and blockers", "Ordered tasks", "Execution notes"):
            self.assertRegex(self.skill_text, rf"##[^\n]*{re.escape(section)}")
        for field in (
            "Objective", "Repository area", "Expected changes/scope",
            "Known files/artifacts", "Dependencies", "Validation",
        ):
            self.assertIn(f"**{field}:**", self.skill_text)

    def test_examples_cover_all_required_categories(self):
        for phrase in ("Small RFC", "Medium RFC", "Large RFC", "Material unresolved detail", "Dependencies:", "Validation:", "RFC §"):
            self.assertIn(phrase, self.examples_text)
        self.assertGreaterEqual(self.examples_text.count("### Task 1:"), 3)
        self.assertIn("parallel", self.examples_text.lower())
        self.assertIn("clarification", self.examples_text.lower())

        task_blocks = re.split(r"(?=### Task \d+:)", self.examples_text)
        task_blocks = [block for block in task_blocks if block.startswith("### Task ")]
        self.assertEqual(len(task_blocks), 6)
        for block in task_blocks:
            self.assertIn("**Known files/artifacts:**", block)
            self.assertNotIn("**Expected writable outputs:**", block)

    def test_exact_worker_allowlist_is_left_to_execution(self):
        self.assertRegex(
            self.skill_text,
            r"(?i)do not require an exhaustive exact-path allowlist",
        )
        self.assertRegex(
            self.skill_text,
            r"(?i)pre-dispatch normalization step owns the exact writable path allowlist",
        )
        self.assertRegex(self.skill_text, r"(?i)do not guess filenames")
        self.assertNotIn("Expected writable outputs", self.skill_text)


if __name__ == "__main__":
    unittest.main()
