---
name: review-fix-loop
description: >-
  Run repeated review and fix rounds on local code changes or a pull request.
  Dispatch the reviewer profile for read-only review; the main agent fixes findings.
  Accept an optional positional maximum loop count and PR URL. Only use this skill
  when explicitly invoked via /review-fix-loop; do not trigger automatically.
---

# Review Fix Loop

## Inputs

Read positional arguments from the invocation, not named parameters:

```text
/review-fix-loop
/review-fix-loop 3
/review-fix-loop https://github.com/org/repo/pull/123
/review-fix-loop 5 https://github.com/org/repo/pull/123
```

Accept exactly `[max-loops] [PR URL]`. The optional first argument is a positive
integer. The optional PR URL may appear alone or after the count. With no count,
there is no numeric cap: continue until the reviewer returns no findings, subject
to the blocking and interruption rules below. With no URL, review local changes.

Reject zero, negative or fractional counts, named parameters, extra arguments,
reversed argument order, and invalid PR URLs before starting. A bare PR number
is not supported as a PR identifier: a lone positive integer means the loop count.
Accept an HTTP(S) URL identifying a specific pull request on the repository's
hosting service; resolve its repository, base, and head using available tooling.
If the URL cannot be validated or accessed, stop with an explanation.

One loop is one reviewer call followed, when findings exist, by main-agent fixes
and relevant verification. A maximum of X loops means at most X reviewer calls.
There is no separate final review, including after the last allowed fix pass.

## Resolve and preserve the scope

1. Read applicable repository guidance and use `project-coding-guidelines` for fixes.
2. Record the starting repository, branch, HEAD, worktree state, and review scope.
   Preserve existing user changes; never reset, discard, or overwrite them.
3. For local changes, include staged, unstaged, and relevant non-ignored untracked
   files. Keep the starting HEAD as the baseline throughout the loop. If there
   are no changes to review, stop and report that; do not claim a clean review.
4. For a PR, resolve the repository, base, head, and merge-base. Review the PR's
   full changes against that fixed merge-base plus fixes made during this run.
   Verify the checkout matches the PR head before editing. If it does not, use
   an isolated checkout/worktree when supported and authorized; otherwise pause
   for a safe checkout decision. Do not switch branches over existing changes.
   Keep unrelated local changes out of the PR scope; pause if they overlap and
   cannot safely be separated. Never edit a different branch as a substitute.
5. Keep the original scope and baseline stable across rounds, adding files needed
   for fixes and tests. Review the entire current scoped diff on every round,
   not merely the latest fix. Allow surrounding code inspection for context.
6. Do not automatically commit, push, post PR comments, or change PR metadata.

## Run each round

### 1. Review through `@reviewer`

Dispatch a fresh subagent through the named `reviewer` profile using the harness's
native agent selection field. The profile owns model selection; do not hard-code
a model or substitute the main agent or another profile. If unavailable, stop
with `MISSING_AGENT_PROFILE: reviewer`.

Pass the reviewer:

- Repository and working directory, applicable guidance, and user requirements.
- Original scope, fixed baseline, and how to inspect the full current scoped diff,
  including untracked files and uncommitted fixes.
- Previous findings, fixes, disputed findings with evidence, and verification
  results. Ask for independent reassessment, not acceptance of the main agent's
  conclusions.
- Instructions to load and use the `code-review` skill before reviewing. The
  reviewer must invoke the skill-loading tool itself; mentioning the skill name
  is not sufficient. If skill loading is unavailable, provide the complete
  `code-review` skill instructions in the reviewer context. If neither is
  possible, stop as blocked rather than perform an unguided review. Apply that
  skill to report only actionable evidence-backed findings and inspect relevant
  feature context and tests.
- Explicit read-only instructions: do not modify files, apply fixes, commit,
  push, or mutate external state. Report checks performed and any review gaps.

Require this handback:

```text
STATUS: NO_FINDINGS | FINDINGS | BLOCKED
FINDINGS:
- ID: stable identifier for tracking across rounds
  Severity: severity with rationale
  Location: file and line/range
  Evidence: concrete failure or contract violation
  Suggested correction: smallest appropriate change
CHECKS: checks performed and results, or not run
REVIEW_GAPS: unavailable context or checks affecting confidence, or none
```

`NO_FINDINGS` requires an empty findings list and an explicit statement that no
actionable findings remain in the reviewed scope. Missing output, tool failure,
contradictory status, or incomplete review is not a clean result. Ask for handback
clarification in the same reviewer session without requesting another review;
if unresolved, stop as blocked. Do not restart review to evade the loop budget.

Count each dispatched review attempt toward the maximum, including failed attempts.
If `NO_FINDINGS` is valid and no material review gap remains, stop as clean.
If `BLOCKED` or a material review gap prevents completion, stop as blocked.

### 2. Main agent fixes

The main agent itself evaluates and fixes findings. Do not delegate fixes to
`executor` or another subagent.

- Confirm each finding against the code and repository contracts before editing.
- Apply the smallest reliable fix for each valid finding, preserving project
  patterns and avoiding unrelated cleanup.
- Use `write-tests` when adding or updating tests and `run-verification` for the
  smallest relevant checks. Load other applicable skills as needed.
- Record each finding as fixed, disputed with evidence, or blocked. Do not silently
  drop findings or declare the review clean based on your own disagreement.
- If a finding needs an unresolved user decision, unsafe/destructive action, or
  unavailable dependency, pause and report the blocker instead of guessing.
- Fix verification failures introduced by the changes before continuing. If
  verification cannot be completed, report the gap; do not imply checks passed.
- Preserve the last review result separately from subsequent edits so the final
  report clearly distinguishes reviewed code from unreviewed fixes.

### 3. Continue or stop

After fixes and verification, if the numeric cap is reached, stop immediately.
Do not dispatch another reviewer, final aggregate review, or confirmation review.
Report: **Loop limit reached; final fixes not re-reviewed.** Include unresolved
findings and verification gaps even if all proposed fixes were applied.

Otherwise start the next round with a fresh reviewer. Omitted count removes only
the numeric cap; it does not permit endless retries when blocked. If the same
finding recurs without substantive progress, pause with evidence and request the
decision needed to proceed. A disputed finding may be reassessed next round, but
repeated disagreement without new evidence is a no-progress blocker.

Honor user interruption immediately and summarize the current state. If outside
changes alter the baseline or overlap the scope during execution, pause to resolve
them rather than silently changing the review target.

## Final report

Keep the report concise and include:

- Status: **clean**, **limit reached**, **blocked**, or **interrupted**. If no local
  changes exist, report **nothing to review** instead.
- Scope: local changes or PR URL, baseline, and working directory if isolated.
- Reviewer calls used and maximum, or no numeric cap.
- Findings fixed, disputed, and unresolved.
- Verification performed, results, and checks not run.
- Whether the latest fixes were reviewed. Only claim clean after an explicit,
  complete reviewer `NO_FINDINGS` result on the current scoped changes.
