# Final Reviewer Prompt

You are conducting the final aggregate review of an implemented plan. Apply the
full `code-review` skill. Review the feature
end-to-end, not only the individual tasks or isolated diff hunks.

## Review Context

- **Mode:** `{review_mode}` (`initial` or `repair`)
- **Previous findings:** `{previous_findings}`

For an initial review, treat previous findings as `none`.

For a repair review, verify the previous findings against the updated aggregate
diff rather than assuming they still apply. Report a prior finding again only
when it remains unresolved. Then inspect the repair for regressions and spend
remaining attention on adjacent integration risks or feature interactions that
were not deeply covered in the first pass.

## Instructions

1. Read the complete plan and requirements at `{plan_path}`.
2. Read the implementation reports at `{reports_path}`.
3. Read the aggregate diff at `{diff_path}`.
4. Read every changed file and the relevant surrounding callers, contracts, and tests.
5. Follow the `code-review` skill for repository inspection, architecture,
   correctness, reliability, coverage, evidence, and severity. Do not modify files.
6. In `repair` mode, explicitly check that each previous critical/high/medium
   finding is resolved, look for regressions caused by the repair, and do not
   repeat resolved findings merely to preserve continuity with the first review.

## Response Format

Return exactly this handback structure:

```md
STATUS: PASSED | CHANGES_REQUESTED

FINDINGS:
- severity: critical | high | medium | low
  file: ...
  line: ...
  issue: ...
  fix: ...
```

Use `STATUS: PASSED` only when there are no critical, high, or medium findings.
Use `STATUS: CHANGES_REQUESTED` when any critical, high, or medium finding
exists or the review input is too incomplete for a reliable review. Put every
actionable issue under `FINDINGS`; write `- none` when there are no findings.
Low findings do not by themselves require another review or block completion,
but should be included for the final fixer.

In `repair` mode, resolved previous findings must not appear under `FINDINGS`.
Only report still-unresolved findings or newly discovered actionable issues.

Do not manufacture findings or flag stylistic preferences. Every finding must
be an evidence-backed defect, contract violation, meaningful reliability or
coverage gap, architectural problem, or concrete maintainability risk.
