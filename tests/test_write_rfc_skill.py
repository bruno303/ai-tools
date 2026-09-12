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
        cls.normalized_skill = re.sub(r"\s+", " ", cls.skill)
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

    def test_workflow_is_repository_first_without_audit_style_labels(self):
        self.assertRegex(self.skill, r"(?i)read.*PRD|PRD.*supporting")
        self.assertRegex(self.skill, r"(?i)repository guidance")
        for concept in (
            "source facts",
            "repository evidence",
            "technical inferences",
            "proposed decisions",
            "assumptions",
            "contradictions",
            "unresolved questions",
        ):
            self.assertIn(concept, self.normalized_skill)
        self.assertRegex(self.skill, r"(?i)do not mechanically label every sentence")

    def test_material_claims_require_flexible_identifiable_attribution(self):
        self.assertRegex(self.skill, r"(?i)cite every material source")
        self.assertRegex(self.skill, r"(?i)document or repository path")
        for locator in ("section", "heading", "symbol", "line/range"):
            self.assertIn(locator, self.skill)
        self.assertIn("`retry-issue.md`, “Retry behavior”", self.examples)
        self.assertIn("`cmd/sync.go`, `RunSync`", self.examples)

    def test_material_uncertainty_is_visibly_separated(self):
        self.assertRegex(
            self.skill,
            r"(?i)assumptions, contradictions, and unresolved decisions visibly",
        )
        self.assertIn("**Contradiction:**", self.examples)
        self.assertIn("**Assumption:**", self.examples)

    def test_clarification_and_draft_behavior_are_explicit(self):
        self.assertRegex(self.skill, r"(?i)only.*material decisions")
        self.assertRegex(self.normalized_skill, r"(?i)batch.*independent.*questions")
        self.assertIn("DRAFT RFC", self.skill)
        self.assertRegex(self.skill, r"(?i)critical decision.*unresolved")

    def test_output_scales_and_stays_out_of_implementation_planning(self):
        self.assertRegex(self.skill, r"(?i)scale.*complexity")
        self.assertIn("flexible pool", self.skill)
        for term in (
            "file-by-file implementation",
            "task batches",
            "executor assignments",
            "worktrees",
            "estimates",
            "coding schedules",
        ):
            self.assertIn(term, self.skill)

    def test_section_pool_covers_separate_design_and_delivery_risks(self):
        self.assertRegex(self.skill, r"(?i)design risks and delivery risks")
        self.assertIn("separate when relevant", self.skill)
        self.assertRegex(self.examples, r"(?i)Design risks")
        self.assertRegex(self.examples, r"(?i)Delivery risks")

    def test_examples_reference_guidance_for_scale_and_decisions(self):
        self.assertIn("references/examples.md", self.skill)
        self.assertRegex(
            self.skill,
            r"(?is)RFC scale,.{0,80}architectural decisions,.{0,80}conflicting sources",
        )

    def test_unfamiliar_reconnaissance_reuses_analyze_codebase(self):
        self.assertIn("analyze-codebase", self.skill)
        self.assertRegex(self.normalized_skill, r"(?i)unfamiliar or non-trivial")
        self.assertRegex(self.normalized_skill, r"(?i)direct reads preferred")
        for model_identifier in ("gpt-5.6", "haiku", "sonnet", "opencode/"):
            self.assertNotIn(model_identifier, self.skill)

    def test_examples_cover_small_large_and_incomplete_sources(self):
        for heading in ("Small feature", "Larger feature", "Incomplete or conflicting"):
            self.assertIn(heading, self.examples)
        self.assertRegex(self.examples, r"(?i)concise RFC")
        self.assertRegex(self.examples, r"(?i)architectural decisions")
        self.assertRegex(self.examples, r"(?i)Batched questions")
        self.assertIn("DRAFT RFC", self.examples)


if __name__ == "__main__":
    unittest.main()
