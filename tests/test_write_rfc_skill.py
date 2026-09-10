import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "write-rfc" / "SKILL.md"
EXAMPLES = ROOT / "skills" / "write-rfc" / "references" / "examples.md"
README = ROOT / "README.md"


class WriteRfcSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.examples = EXAMPLES.read_text(encoding="utf-8")
        cls.readme = README.read_text(encoding="utf-8")

    def test_skill_exists_with_trigger_oriented_frontmatter(self):
        self.assertTrue(SKILL.is_file())
        self.assertRegex(self.skill, r"\A---\s*\nname:\s*write-rfc\s*\n")
        self.assertRegex(self.skill, r"description:.*\b(PRD|issue|requirements)\b")

    def test_readme_places_rfc_between_analysis_and_planning(self):
        analysis = self.readme.index("skills/analyze-codebase/SKILL.md")
        rfc = self.readme.index("skills/write-rfc/SKILL.md")
        planning = self.readme.index("skills/plan-implementation/SKILL.md")
        self.assertLess(analysis, rfc)
        self.assertLess(rfc, planning)

    def test_workflow_is_repository_first_and_classifies_claims(self):
        self.assertRegex(self.skill, r"(?i)read.*PRD|PRD.*supporting")
        self.assertRegex(self.skill, r"(?i)repository guidance")
        for label in ("source fact", "repository evidence", "technical inference",
                      "proposed decision", "assumption", "contradiction",
                      "unresolved question"):
            self.assertIn(label, self.skill)

    def test_material_claims_require_identifiable_source_attribution(self):
        self.assertRegex(self.skill, r"(?i)material.*source fact")
        self.assertRegex(self.skill, r"(?i)repository evidence.*cite")
        self.assertRegex(self.skill, r"(?i)document\s+title/path\s+plus\s+section")
        self.assertRegex(self.skill, r"(?i)repository file\s+plus\s+symbol")
        self.assertIn("source fact", self.examples)
        self.assertIn("repository evidence", self.examples)
        self.assertIn("section", self.examples)
        self.assertIn("`cmd/sync.go`, `RunSync`", self.examples)

    def test_clarification_and_draft_behavior_are_explicit(self):
        self.assertRegex(self.skill, r"(?i)only.*material decisions")
        self.assertRegex(self.skill, r"(?i)batch.*independent.*questions")
        self.assertIn("DRAFT RFC", self.skill)
        self.assertRegex(self.skill, r"(?i)critical decision.*unresolved")

    def test_output_scales_and_stays_out_of_implementation_planning(self):
        self.assertRegex(self.skill, r"(?i)scale.*complexity")
        self.assertIn("flexible pool", self.skill)
        for term in ("file-by-file implementation", "task batches", "executor assignments",
                     "worktrees", "estimates", "coding schedules"):
            self.assertIn(term, self.skill)

    def test_section_pool_covers_separate_design_and_delivery_risks(self):
        self.assertRegex(self.skill, r"(?i)design risks and delivery risks")
        self.assertIn("design risks", self.skill)
        self.assertIn("delivery risks", self.skill)
        self.assertIn("separate when relevant", self.skill)
        self.assertRegex(self.examples, r"(?i)Design risks")
        self.assertRegex(self.examples, r"(?i)Delivery risks")

    def test_examples_reference_guidance_for_scale_and_decisions(self):
        self.assertIn("references/examples.md", self.skill)
        self.assertRegex(self.skill, r"(?is)RFC scale,.{0,80}architectural decisions,.{0,80}conflicting sources")

    def test_examples_cover_small_large_and_incomplete_sources(self):
        for heading in ("Small feature", "Larger feature", "Incomplete or conflicting"):
            self.assertIn(heading, self.examples)
        self.assertRegex(self.examples, r"(?i)concise RFC")
        self.assertRegex(self.examples, r"(?i)architectural decisions")
        self.assertRegex(self.examples, r"(?i)Batched questions")
        self.assertIn("DRAFT RFC", self.examples)


if __name__ == "__main__":
    unittest.main()
