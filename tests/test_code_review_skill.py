import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "code-review" / "SKILL.md"


class CodeReviewSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.normalized = re.sub(r"\s+", " ", cls.skill)
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_frontmatter_and_readme_entry(self):
        self.assertRegex(self.skill, r"\A---\s*\nname: code-review\n")
        self.assertIn("description:", self.skill)
        self.assertIn("skills/code-review/SKILL.md", self.readme)

    def test_findings_survive_a_falsification_pass(self):
        for rule in (
            "## 4. Verify Findings",
            "run a falsification pass over every candidate finding",
            "**Evidence**: the exact line, quote, or command output",
            "**Failure path**: a concrete trigger and the consequence in the current code",
            "If you cannot name a trigger, the item is an observation, not a finding.",
            "**Scope**: whether the problem exists in the current code, or only if the code",
            "**Check**: the cheapest test, `grep`, type check, or call-path inspection",
            "**Reproduced**: a command or test demonstrates the failure.",
            "**Inspected**: the code path and contract prove the failure; no runnable",
            "**Speculative**: plausible, but no concrete trigger in the current code.",
            "Only `Reproduced` and `Inspected` items may be reported as findings.",
            "`Speculative` items are observations at most",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.normalized)

    def test_verifier_is_adversarial(self):
        for rule in (
            "fresh verifier with only",
            "the diff and the findings list",
            "must reproduce each `Reproduced`",
            "claim or mark it `NEEDS-RECHECK`",
            "re-derive each `Inspected` claim from the",
            "Do not give the verifier the original reasoning.",
            "Treat a `NEEDS-RECHECK` result as unverified",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.normalized)

    def test_finding_format_and_two_tier_output(self):
        for rule in (
            "**Failure path:**",
            "**Evidence grade:**",
            "**Check:**",
            "**Scope:**",
            "List only `Reproduced` and `Inspected` findings, ordered by severity",
            "## Observations",
            "List `Speculative` items and latent risks",
            "Do not assign severity or request changes for them.",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.normalized)

    def test_principles_prefer_verified_findings(self):
        for rule in (
            "Prefer a smaller, verified report over a larger, plausible one.",
            "A finding without a concrete failure path is an observation, not a finding.",
            "Do not use a confidence number as a substitute for evidence.",
            "Do not manufacture findings to make the review appear thorough.",
            "A clean review is a valid result.",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.normalized)

    def test_latent_risks_are_observations_not_findings(self):
        self.assertIn(
            "If the consequence only exists after a future change to the code or protocol, "
            "record it as an observation instead of a finding.",
            self.normalized,
        )


if __name__ == "__main__":
    unittest.main()
