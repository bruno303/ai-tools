import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "skills" / "plan-implementation" / "SKILL.md"
PREPARE = ROOT / "skills" / "prepare-pr-review" / "SKILL.md"
REVIEW = ROOT / "skills" / "code-review" / "SKILL.md"


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text)


class DesignArtifactsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = PLAN.read_text(encoding="utf-8")
        cls.plan_flat = normalize(cls.plan)
        cls.prepare = PREPARE.read_text(encoding="utf-8")
        cls.prepare_flat = normalize(cls.prepare)
        cls.review = REVIEW.read_text(encoding="utf-8")
        cls.review_flat = normalize(cls.review)
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_plan_records_pattern_decision_only_against_a_named_force(self):
        for rule in (
            "# Pattern decision gate",
            "Record a pattern only when a force exists",
            "explicit `none` is a valid and frequent answer",
            "- force:",
            "- response:",
            "- cost / rejected:",
            "A force is concrete when it names what breaks without the pattern",
            "- No named force, no pattern.",
            "These are not forces",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.plan_flat)

    def test_plan_bounds_pattern_ceremony_and_marks_deviations(self):
        for rule in (
            "- At most two patterns.",
            "A pattern the repository does not already use is a deviation",
            "Record it as a deviation with the reason",
            "never introduce it silently",
            "`cost / rejected` is mandatory",
            "If an approved RFC or design document already settles the pattern",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.plan_flat)

    def test_plan_pattern_decision_is_a_review_criterion(self):
        self.assertIn(
            "The recorded decision is a review criterion: `code-review` checks the "
            "code against it, and a silent divergence is a finding.",
            self.plan_flat,
        )
        self.assertIn("including the pattern decision or an explicit `none`", self.plan_flat)

    def test_prepare_pr_review_caps_diagrams_and_their_purpose(self):
        for rule in (
            "## Diagrams",
            "Use at most two diagrams",
            "### Component diagram",
            "Box = module, boundary, or process. Arrow = dependency direction.",
            "3 to 12 nodes.",
            "One edge per real dependency, not per call.",
            "### Sequence diagram",
            "Include the partial-failure branch",
            "Stop at component boundaries",
            "Do not draw files, functions, or classes",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.prepare_flat)

    def test_prepare_pr_review_distinguishes_derived_from_approved_diagrams(self):
        for rule in (
            "Prefer the diagram from the implementation plan or RFC",
            "Derived from the diff at review time, not an approved design.",
            "launders uncertainty into apparent fact",
            "Never present a diff-derived diagram as if it were the approved structure",
            "surface it under **Decisions to validate**",
            "## Principles",
            "Never present a diff-derived diagram as the approved design.",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.prepare_flat)

    def test_prepare_pr_review_requires_rendering_evidence(self):
        for rule in (
            "Both diagrams must render.",
            "Mermaid fails silently",
            "mmdc -i diagram.mmd -o diagram.svg",
            "say the rendering is unverified",
            "also place it in the repository",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.prepare_flat)

    def test_code_review_compares_code_against_recorded_artifacts(self):
        for rule in (
            "### Compare against recorded design artifacts",
            "Does the code implement the pattern selected for the named force",
            "Does dependency direction in the code match the component diagram?",
            "Does the flow match the sequence diagram",
            "Silence is the failure mode; deviation is not.",
            "When no artifact exists, review the structure on its own merits",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.review_flat)

    def test_readme_advertises_the_new_behavior(self):
        for phrase in (
            "force-gated pattern decision",
            "Mermaid component and sequence diagrams",
            "conformance to recorded pattern decisions and diagrams",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.readme)


if __name__ == "__main__":
    unittest.main()
