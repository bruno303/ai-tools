---
name: run-verification
description: Use when validating a code change by running the smallest relevant checks first, then expanding verification only as needed. Conditionally check Sonar findings when the repository and available MCP tools are configured for Sonar analysis.
---

# When to use
Use for:
- validating an implementation before presenting it
- verifying a bug fix or refactor
- checking whether a suspected issue is reproduced by tests or tooling

Do not use for:
- planning work before code changes
- code review without running any commands

# Goal
Verify changes efficiently without wasting time or tokens on unnecessary full-suite runs.

# Core principle
Evidence before claims. Do not claim that work is complete, fixed, passing, or regression-free without fresh verification evidence from the current change.

# Process
1. Identify the exact proof command for the claim being evaluated.
2. Start with the smallest relevant verification scope.
3. Run targeted tests closest to the changed behavior.
4. Run format, lint, typecheck, or build steps only if relevant.
5. Expand to broader verification if targeted checks fail to provide confidence.
6. Read the complete output and confirm the command's exit status.
7. Check Sonar analysis when it is available, following the conditional process below.
8. Record what was run and what was not.

# Conditional Sonar Verification
After local checks, determine whether Sonar verification is available:

1. Inspect the repository for Sonar configuration, such as `sonar-project.properties`, scanner configuration, or Sonar CI workflow steps.
2. Inspect the available tool catalog for Sonar MCP tools.
3. If either is absent, do not attempt a substitute remote scan. Record Sonar as unavailable and continue.
4. If both are available, retrieve findings for the current branch or pull request and its current revision. Do not treat historical or default-branch findings as regressions in the current change.
5. When the current analysis is complete, remediate actionable findings introduced by the change when practical, then rerun the smallest relevant local checks.
6. When analysis is pending for an active pull request workflow, wait up to 60 seconds for completion. If it remains pending, stop waiting and report the pending state with the available PR or analysis link.
7. Outside a pull request workflow, do not wait for asynchronous analysis. Report it as pending after local verification.

Sonar is asynchronous. Never describe a change as Sonar-clean unless a completed analysis for the current branch or pull request revision has no applicable open findings.

# Rules
- Prefer narrow verification first.
- Run the proof command fresh for the current change; prior output, assumptions, or agent reports are not evidence.
- Do not claim a check passed unless it was actually run and its output and exit status support that claim.
- Ensure completion, fix, and regression claims match the scope of the evidence; passing a targeted check does not prove the full suite passes.
- Report skipped checks explicitly.
- When a command fails, summarize the failure and likely cause.
- Report Sonar status as `clean`, `findings`, `pending`, or `unavailable`.

# Output
Provide:
- commands run
- pass/fail result for each
- notable failures or warnings
- checks not run
- Sonar status, analysis scope, and any pending-analysis link
