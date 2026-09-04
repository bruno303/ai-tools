# Final Fixer Prompt

You are performing the single final fix pass for an implemented plan. Resolve
the supplied review findings without expanding the approved scope.

## Inputs

1. Read the complete plan at `{plan_path}`.
2. Read all implementation reports at `{reports_path}`.
3. Read the aggregate diff at `{diff_path}`.
4. Read the complete final reviewer handback and address every critical, high,
   and medium finding, plus practical low findings:

```text
{findings}
```

5. Modify only the expected output paths:

```text
{expected_outputs}
```

## Verification and Report

Run every resolved applicable verification command:

```text
{verify_commands}
```

Fix failures within the approved scope before reporting completion. Write a
concise report to `{report_path}` containing the files changed, findings
addressed, and every verification command with its result. If a command is
unavailable or not applicable, record that explicitly rather than claiming it
passed.

## Response Format

Return exactly:

```md
STATUS: OK | BLOCKED

FILES_MODIFIED:
- ...

FIX_SUMMARY:
- ...

VERIFICATION:
- command: ...
  result: passed | failed | unavailable | not_applicable
  notes: ...

BLOCKERS:
- none
```

Return `STATUS: BLOCKED` when the findings cannot be resolved safely within
scope, required context is missing, or verification exposes an unresolved
problem. Do not guess.
