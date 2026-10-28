import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
PLAN = SKILLS / "plan-implementation" / "SKILL.md"
OPEN_PR = SKILLS / "open-pr" / "SKILL.md"
PREPARE = SKILLS / "prepare-pr-review" / "SKILL.md"
REVIEW = SKILLS / "code-review" / "SKILL.md"


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text)


class DesignArtifactsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = normalize(PLAN.read_text(encoding="utf-8"))
        cls.open_pr = normalize(OPEN_PR.read_text(encoding="utf-8"))
        cls.prepare = normalize(PREPARE.read_text(encoding="utf-8"))
        cls.review = normalize(REVIEW.read_text(encoding="utf-8"))
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
                self.assertIn(rule, self.plan)

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
                self.assertIn(rule, self.plan)

    def test_plan_pattern_decision_is_a_review_criterion(self):
        self.assertIn(
            "The recorded decision is a review criterion: `code-review` checks the "
            "code against it, and a silent divergence is a finding.",
            self.plan,
        )
        self.assertIn("including the pattern decision or an explicit `none`", self.plan)

    def test_plan_authors_the_diagrams_instead_of_deferring_them(self):
        for rule in (
            "# Diagrams",
            "Author the component and sequence diagrams here, while planning — "
            "not at PR time.",
            "3 to 12 nodes",
            "including the partial-failure branch",
            "Validate that each Mermaid block renders before finalizing the plan.",
            "`open-pr` copies these into the PR body",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.plan)
        self.assertIn(
            "component and sequence diagrams, unless the change is localized enough",
            self.plan,
        )

    def test_open_pr_owns_the_author_side_body(self):
        for rule in (
            "name: open-pr",
            "Omit a section rather than fill it.",
            "### Why",
            "### What changed",
            "### Risk and blast radius",
            "### Verification",
            "Draft `Why`, then `What changed`, then the rest.",
            "One PR, one reviewable intent.",
            "Never claim a check you did not run",
            "--body-file body.md",
            "Never present a diagram written after the fact as the approved design.",
            "mmdc -i diagram.mmd -o diagram.svg",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.open_pr)

    def test_open_pr_points_at_the_review_side_instead_of_duplicating_it(self):
        for rule in (
            "This skill owns the author side.",
            "To review someone else's PR, use `prepare-pr-review`.",
            "the full reading guide belongs to `prepare-pr-review`",
            "state the divergence and the reason",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.open_pr)

    def test_prepare_pr_review_treats_diagrams_as_optional_aids(self):
        for rule in (
            "## Diagrams",
            "A diagram is a review aid, not a requirement.",
            "Never treat its absence as a finding",
            "build one if the change is easier to explain that way",
            "Reconstructed from the diff, not the approved design.",
            "a component view (modules and dependency direction, 3 to 12 nodes)",
            "report divergence under **Decisions to validate**",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.prepare)
        for forbidden in ("A missing diagram is a finding", "do not manufacture one"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.prepare)

    def test_code_review_treats_artifacts_as_optional_evidence(self):
        for rule in (
            "### Compare against recorded design artifacts, when they exist",
            "Does the code implement the pattern selected for the named force",
            "Does dependency direction in the code match the component diagram?",
            "Does the flow match the sequence diagram",
            "That is not a gap to report.",
            "do not require a plan, a pattern decision, or a diagram before reviewing",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.review)
        for forbidden in ("Silence is the failure mode",):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.review)

    def test_readme_lists_the_artifact_pipeline_in_order(self):
        for phrase in (
            "force-gated pattern decision",
            "`skills/open-pr/SKILL.md`",
            "diagrams where useful",
            "using recorded plans and diagrams as evidence when present",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.readme)

        plan_at = self.readme.index("skills/plan-implementation/SKILL.md")
        open_pr_at = self.readme.index("skills/open-pr/SKILL.md")
        review_at = self.readme.index("skills/code-review/SKILL.md")
        prepare_at = self.readme.index("skills/prepare-pr-review/SKILL.md")
        self.assertLess(plan_at, open_pr_at)
        self.assertLess(open_pr_at, review_at)
        self.assertLess(review_at, prepare_at)


if __name__ == "__main__":
    unittest.main()
