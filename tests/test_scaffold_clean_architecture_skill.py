import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "scaffold-clean-architecture" / "SKILL.md"
README = ROOT / "README.md"


class ScaffoldCleanArchitectureSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.normalized_skill = re.sub(r"\s+", " ", cls.skill)
        cls.readme = README.read_text(encoding="utf-8")

    def test_skill_exists_with_trigger_oriented_frontmatter(self):
        self.assertTrue(SKILL.is_file())
        self.assertRegex(self.skill, r"\A---\s*\nname:\s*scaffold-clean-architecture\s*\n")
        self.assertRegex(self.skill, r"description:.*\bbrand-new projects\b")

    def test_scope_is_limited_to_new_projects(self):
        self.assertIn("Adding a service, module, or component to an existing repository", self.normalized_skill)
        self.assertIn("brand-new project", self.skill)
        self.assertNotIn("The project, service, or module does not exist yet", self.skill)

    def test_ports_are_declared_where_consumed(self):
        self.assertIn("declared by the layer that consumes them", self.normalized_skill)
        self.assertIn("go-expert", self.skill)
        self.assertIn("places repository and client contracts under `domain/`", self.normalized_skill)
        self.assertNotIn("Ports (interfaces) live in `application`.", self.skill)
        self.assertNotIn("Ports declared in `application`", self.skill)

    def test_entrypoints_are_not_a_test_layer(self):
        self.assertIn("Entrypoints are not a test layer", self.skill)
        self.assertIn("test-specific entrypoint", self.normalized_skill)
        self.assertNotIn("one thin smoke test", self.skill)

    def test_vertical_slice_and_executable_enforcement_are_required(self):
        for phrase in (
            "Build one vertical slice",
            "One vertical slice works end-to-end",
            "fails the build on a backward dependency",
            "A rule without a failing build is a suggestion.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.normalized_skill)

    def test_reference_file_was_removed_and_readme_lists_the_skill(self):
        self.assertFalse((SKILL.parent / "references").exists())
        self.assertIn("skills/scaffold-clean-architecture/SKILL.md", self.readme)


if __name__ == "__main__":
    unittest.main()
