import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "software-design"
SKILL = SKILL_DIR / "SKILL.md"
PATTERNS = SKILL_DIR / "references" / "patterns.md"
SOLID = SKILL_DIR / "references" / "solid.md"
SELECTION = SKILL_DIR / "references" / "pattern-selection.md"
README = ROOT / "README.md"

PATTERN_NAMES = (
    "Strategy",
    "Decorator",
    "Repository",
    "Singleton",
    "Factory",
    "Builder",
    "Adapter",
    "Chain of Responsibility",
    "State",
    "Observer / Events",
    "Middleware",
    "Value Object",
    "Unit of Work",
    "Dependency Injection",
)

PATTERN_FIELDS = (
    "Intent.",
    "Problem / force.",
    "Use when.",
    "Avoid when.",
    "Structure.",
    "Tradeoffs.",
    "Common misuse.",
    "Related SOLID.",
    "Sketch.",
)


class SoftwareDesignSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.patterns = PATTERNS.read_text(encoding="utf-8")
        cls.solid = SOLID.read_text(encoding="utf-8")
        cls.selection = SELECTION.read_text(encoding="utf-8")
        cls.readme = README.read_text(encoding="utf-8")

    def test_skill_exists_with_matching_frontmatter_name(self):
        self.assertTrue(SKILL.is_file())
        self.assertRegex(self.skill, r"\A---\s*\nname:\s*software-design\s*\n")
        self.assertRegex(self.skill, r"description:\s*.+\n---")
        self.assertEqual(SKILL.parent.name, "software-design")

    def test_referenced_files_exist_and_are_linked(self):
        references = set(re.findall(r"`references/([^`]+\.md)`", self.skill))
        self.assertEqual(
            references,
            {"solid.md", "patterns.md", "pattern-selection.md", "review-checklist.md"},
        )
        for name in references:
            with self.subTest(reference=name):
                self.assertTrue((SKILL_DIR / "references" / name).is_file())

    def test_catalog_covers_all_patterns_with_the_same_fields(self):
        sections = re.split(r"(?m)^## ", self.patterns)[1:]
        headings = [section.splitlines()[0].strip() for section in sections]
        for pattern in PATTERN_NAMES:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, headings)

        by_heading = {section.splitlines()[0].strip(): section for section in sections}
        for pattern in PATTERN_NAMES:
            with self.subTest(pattern=pattern):
                section = by_heading[pattern]
                for field in PATTERN_FIELDS:
                    self.assertIn(f"**{field}**", section)

    def test_solid_is_presented_with_counterweights(self):
        for principle in (
            "Single Responsibility Principle",
            "Open/Closed Principle",
            "Liskov Substitution Principle",
            "Interface Segregation Principle",
            "Dependency Inversion Principle",
        ):
            with self.subTest(principle=principle):
                self.assertIn(principle, self.solid)
        self.assertIn("When not to apply.", self.solid)
        self.assertIn("Counterweight.", self.solid)
        self.assertIn("Using SOLID without over-abstracting", self.solid)

    def test_selection_guide_starts_from_forces_and_keeps_no_pattern_valid(self):
        for pattern in PATTERN_NAMES:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, self.selection)
        for discriminator in (
            "Strategy vs State",
            "Adapter vs Decorator vs Middleware",
            "Repository vs direct data access",
            "Factory vs Builder",
            "Chain of Responsibility vs Middleware vs Observer",
        ):
            with self.subTest(discriminator=discriminator):
                self.assertIn(discriminator, self.selection)
        self.assertIn("No pattern", self.selection)
        self.assertIn("Direct implementation", self.selection)

    def test_development_skills_point_to_the_canonical_skill(self):
        pointers = {
            "skills/project-coding-guidelines/SKILL.md": "software-design",
            "skills/plan-implementation/SKILL.md": "software-design",
            "skills/analyze-codebase/SKILL.md": "software-design",
            "skills/code-review/SKILL.md": "software-design",
            "skills/go-expert/SKILL.md": "software-design",
            "skills/nextjs-coding/SKILL.md": "software-design",
            "skills/subagent-plan-execution/references/final_reviewer_prompt.md": "software-design",
            "README.md": "skills/software-design/SKILL.md",
        }
        for relative, pointer in pointers.items():
            with self.subTest(file=relative):
                text = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn(pointer, text)

    def test_skill_does_not_hard_code_models(self):
        for model_identifier in ("gpt-5.6", "haiku", "sonnet", "opencode/"):
            with self.subTest(model_identifier=model_identifier):
                self.assertNotIn(model_identifier, self.skill)


if __name__ == "__main__":
    unittest.main()
