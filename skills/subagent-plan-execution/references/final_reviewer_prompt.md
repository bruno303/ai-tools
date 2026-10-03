# Final Reviewer Prompt

You are conducting the final aggregate review of an implemented plan. Apply the
full `code-review` skill. Review the feature
end-to-end, not only the individual tasks or isolated diff hunks.

## Instructions

1. Read the complete plan and requirements at `{plan_path}`.
2. Read the implementation reports at `{reports_path}`.
3. Read the aggregate diff at `{diff_path}`.
4. Read every changed file and the relevant surrounding callers, contracts, and tests.
   Check the aggregate diff against the plan's constraints, non-goals, and
   acceptance evidence, including negative constraints and behavior-affecting
   defaults.
5. Follow the `code-review` skill for repository inspection, architecture,
   correctness, reliability, coverage, evidence, and severity. Do not modify files.
6. Support every finding with concrete evidence: the exact file and symbol or
   line, plus the spec, contract, or baseline behavior it violates. Verify
   baseline behavior before calling something a regression; do not attribute
   unchanged pre-existing behavior to the change without evidence that the change
   introduces or exposes it.

## Response Format

Return exactly this handback structure:

```md
STATUS: PASSED | CHANGES_REQUESTED

FINDINGS:
- severity: critical | high | medium | low
  file: ...
  line: ...
  issue: ...
  evidence: ...
  fix: ...
```

Use only those two status values. A missing, malformed, or different status is a
protocol failure; never report or infer a pass from an ambiguous verdict.

Use `STATUS: PASSED` only when there are no critical, high, or medium findings.
Use `STATUS: CHANGES_REQUESTED` when any critical, high, or medium finding
exists or the review input is too incomplete for a reliable review. Put every
actionable issue under `FINDINGS`; write `- none` when there are no findings.
Low findings do not by themselves require another review or block completion,
but should be included for the final fixer.

Do not manufacture findings or flag stylistic preferences. Every finding must
be an evidence-backed defect, contract violation, meaningful reliability or
coverage gap, architectural problem, or concrete maintainability risk.
