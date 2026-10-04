import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "review-fix-loop" / "SKILL.md"


class ReviewFixLoopSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.normalized = re.sub(r"\s+", " ", cls.skill)

    def test_frontmatter_and_explicit_invocation(self):
        self.assertRegex(self.skill, r"\A---\s*\nname: review-fix-loop\n")
        self.assertIn("description:", self.skill)
        self.assertIn("when explicitly invoked via /review-fix-loop", self.normalized)
        self.assertIn("do not trigger automatically", self.normalized)
        self.assertIn("skills/review-fix-loop/SKILL.md", (ROOT / "README.md").read_text())

    def test_positional_inputs_and_validation(self):
        for invocation in (
            "/review-fix-loop\n",
            "/review-fix-loop 3\n",
            "/review-fix-loop https://github.com/org/repo/pull/123",
            "/review-fix-loop 5 https://github.com/org/repo/pull/123",
        ):
            self.assertIn(invocation, self.skill)
        for rule in (
            "positive integer", "no numeric cap", "zero, negative or fractional",
            "named parameters, extra arguments", "reversed argument order",
            "invalid PR URLs", "a lone positive integer means the loop count",
        ):
            self.assertIn(rule, self.normalized)

    def test_roles_and_review_handback(self):
        for rule in (
            "fresh subagent", "named `reviewer` profile", "MISSING_AGENT_PROFILE: reviewer",
            "do not modify files", "The main agent itself evaluates and fixes findings",
            "Do not delegate fixes", "STATUS: NO_FINDINGS | FINDINGS | BLOCKED",
            "Evidence:", "REVIEW_GAPS:", "independent reassessment",
        ):
            self.assertIn(rule, self.normalized)
        for model in ("gpt-5.6", "haiku", "sonnet", "opencode/"):
            self.assertNotIn(model, self.skill)

    def test_budget_and_truthful_stop_rules(self):
        for rule in (
            "at most X reviewer calls", "including failed attempts",
            "There is no separate final review", "stop immediately",
            "Loop limit reached; final fixes not re-reviewed.",
            "same finding recurs without substantive progress",
            "Honor user interruption immediately", "not a clean result",
            "Only claim clean after an explicit",
        ):
            self.assertIn(rule, self.normalized)

    def test_scope_preservation_and_verification(self):
        for rule in (
            "staged, unstaged", "untracked", "fixed merge-base",
            "checkout matches the PR head", "unrelated local changes",
            "entire current scoped diff", "never reset, discard, or overwrite",
            "Do not automatically commit, push, post PR comments",
            "write-tests", "run-verification", "nothing to review",
        ):
            self.assertIn(rule, self.normalized)


if __name__ == "__main__":
    unittest.main()
