import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "grill-me" / "SKILL.md"


class GrillMeSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.normalized_skill = re.sub(r"\s+", " ", cls.skill)

    def test_skill_reuses_shared_reconnaissance_path(self):
        self.assertTrue(SKILL.is_file())
        self.assertIn("analyze-codebase", self.skill)
        self.assertRegex(self.skill, r"(?i)unfamiliar or non-trivial")
        self.assertRegex(self.normalized_skill, r"(?i)direct reads (?:remain )?preferred")
        self.assertRegex(self.skill, r"(?i)delegation.*unavailable")

    def test_reader_contract_is_not_duplicated_or_model_bound(self):
        for model_identifier in ("gpt-5.6", "haiku", "sonnet", "opencode/"):
            self.assertNotIn(model_identifier, self.skill)
        for phrase in ("fresh named `codebase-reader`", "facts versus hypotheses", "handback"):
            self.assertNotIn(phrase, self.normalized_skill)


if __name__ == "__main__":
    unittest.main()
