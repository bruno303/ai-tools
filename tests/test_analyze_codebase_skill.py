import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "analyze-codebase" / "SKILL.md"


class AnalyzeCodebaseSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.normalized_skill = re.sub(r"\s+", " ", cls.skill)

    def test_skill_exists_with_expected_frontmatter(self):
        self.assertTrue(SKILL.is_file())
        self.assertRegex(self.skill, r"\A---\s*\nname:\s*analyze-codebase\s*\n")
        self.assertRegex(self.skill, r"description:\s*.+\n---")

    def test_delegation_is_optional_and_task_directed(self):
        for phrase in (
            "non-trivial",
            "fresh named `codebase-reader`",
            "concrete user task",
            "repository root",
            "known scope",
            "user's constraints",
            "only enough context",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.skill)
        self.assertRegex(self.skill, r"(?i)delegation is optional")
        self.assertRegex(self.skill, r"(?i)not an exhaustive repository survey")

    def test_unresolved_profile_falls_back_to_parent_analysis(self):
        self.assertRegex(self.skill, r"(?i)profile cannot be resolved")
        self.assertRegex(self.skill, r"(?i)perform the same analysis in the parent")
        self.assertRegex(self.skill, r"(?i)rather than failing")

    def test_reader_handback_covers_required_context(self):
        for phrase in (
            "relevant files and modules",
            "current flow summary",
            "boundaries and dependencies involved",
            "existing patterns to follow",
            "likely change points",
            "questions, contradictions, and risks",
            "facts versus hypotheses",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.skill)
        self.assertRegex(self.skill, r"(?i)parent.*responsible.*verif")

    def test_model_selection_is_not_hard_coded_and_scope_stays_limited(self):
        self.assertIn("never make model selection part of this skill", self.skill)
        self.assertRegex(self.skill, r"(?i)hard-code a model")
        self.assertRegex(self.normalized_skill, r"(?i)relevant scope")
        self.assertRegex(self.normalized_skill, r"(?i)enough evidence")
        for model_identifier in ("gpt-5.6", "haiku", "sonnet", "opencode/"):
            with self.subTest(model_identifier=model_identifier):
                self.assertNotIn(model_identifier, self.skill)


if __name__ == "__main__":
    unittest.main()
