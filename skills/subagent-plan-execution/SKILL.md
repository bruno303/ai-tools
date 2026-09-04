---
name: subagent-plan-execution
description: Execute an existing implementation plan by dispatching fresh subagents per task, with mandatory spec-compliance and code-quality review gates. Only use this skill when explicitly invoked via /subagent-plan-execution — do NOT trigger automatically based on context or user phrasing.
---

# Subagent Plan Execution

Execute a multi-task implementation plan by dispatching each task to a fresh subagent with zero context pollution. Each task gets a lightweight implementation gate; after all tasks, one fresh reviewer applies the full `code-review` skill to the aggregate change, followed by one consolidated fix pass and a non-looping quality gate.

## Locating Reference Files

This SKILL.md lives in a skill directory. Its sibling `references/` folder contains the implementer and reviewer prompt templates. If you loaded this skill from a file path, resolve paths relative to that directory. If unsure, search your filesystem for `implementer_prompt.md` — it lives next to this file.

## Step 0: Load the Plan

If the plan already exists as a file (e.g., `plan.md`, `.agents/plans/plan.md`), read it once.

If the plan exists only in the conversation, write it to `.agents/plans/plan.md` first. Use a flexible format — the only requirement is that tasks are clearly separated and each has enough detail for someone unfamiliar with the project to implement it. Example:

```markdown
# Plan: Feature Name

## Task 1: Add user authentication
**Files:** src/auth/login.ts, src/auth/middleware.ts
**Dependencies:** none

Implement JWT-based login endpoint at POST /auth/login...

## Task 2: Protect routes
**Files:** src/middleware/guard.ts
**Dependencies:** Task 1
...
```

Read the plan once, build an internal task list, then close the file. Don't keep re-reading it.

## Step 1: Execute Each Task

Work through tasks one at a time (or in parallel if they touch different files with no dependencies). For single-task plans, just run one cycle.

For each task, do the following in order. Skipping any substep breaks the review loop — a subagent dispatched without a brief file has no spec to implement against.

### 1a. Write the Brief File

The brief file is the contract between you, the implementer, and the reviewer. Create `.agents/plans/task-N-brief.md` containing the task spec verbatim from the plan. Nothing else.

```
mkdir -p .agents/plans
cat > .agents/plans/task-N-brief.md << 'EOF'
<task spec from the plan>
EOF
```

**Verify it exists** before proceeding. If you can't write files, use your platform's Write tool. This step is not optional — without the brief file, the implementer has no spec and the reviewer has nothing to check against.

### 1b. Dispatch the Implementer

Read the template at `references/implementer_prompt.md` (in the skill directory). Fill in these placeholders:

| Placeholder | Value |
|---|---|
| `{brief_path}` | `.agents/plans/task-N-brief.md` |
| `{report_path}` | `.agents/plans/task-N-report.md` |
| `{language}` | Python, Go, TypeScript, etc. |
| `{test_dir}` | Where tests live |
| `{conventions}` | Imports, naming, error handling style — whatever matters |
| `{verify_command}` | Exact command (e.g., `go build ./... && go test ./...`) |
| `{expected_outputs}` | Files to create or modify |
| `{commit_format}` | Only if committing, e.g., `feat(task-N): message` |

Dispatch a fresh subagent with the filled-in template. Give it the project root path so it can resolve `{brief_path}`. Do not paste the full plan or spec into the dispatch prompt — that's what the brief file is for.

#### Result Handling

| Response | Action |
|---|---|
| **DONE** | Proceed to 1c. |
| **BLOCKED: \<reason\>** | Fix the blocker (add context, clarify spec, split task) and re-dispatch from 1b once. If the retry is blocked, stop the task and report the unresolved blocker; do not retry indefinitely. |

### 1c. Lightweight Implementation Review

First, verify the implementer's claimed outputs exist:

```
ls -la <each file in expected_outputs>
```

If any file is missing, re-dispatch once with the exact path correction. If an
expected output is still missing after that retry, stop the task and report the
unresolved output; do not retry indefinitely.

Generate a diff package so the reviewer reads one file. Use the working-tree
diff when the implementer did not commit. If it did commit, use the latest
commit instead of assuming a parent commit exists:

```
if git diff --quiet HEAD; then
  git show --stat --format=oneline HEAD > .agents/plans/review-task-N.diff
  git show --format= --no-ext-diff HEAD >> .agents/plans/review-task-N.diff
else
  git diff --stat HEAD > .agents/plans/review-task-N.diff
  git diff -U10 HEAD >> .agents/plans/review-task-N.diff
fi
```

(Without git, collect changed file paths and their contents into `.agents/plans/review-task-N.diff`.)

Read `references/reviewer_prompt.md` (in the skill directory). This is a
lightweight task gate, not the full code review. It checks the task contract,
obvious correctness issues, and focused test/verification coverage. Fill in:

| Placeholder | Value |
|---|---|
| `{brief_path}` | `.agents/plans/task-N-brief.md` |
| `{report_path}` | `.agents/plans/task-N-report.md` |
| `{diff_path}` | `.agents/plans/review-task-N.diff` |

Dispatch one fresh reviewer subagent. Do not perform broad architectural or
end-to-end review here; that happens once after all tasks are complete.

#### Result Handling

| Response | Action |
|---|---|
| **`STATUS: PASSED`** | No blocking findings. Move to the quality gate for this task, then continue to the next task. |
| **`STATUS: CHANGES_REQUESTED`** | Reviewer listed a task-level defect. Dispatch one fresh implementer for a single consolidated fix pass containing the findings. The fix pass must write an updated report and run the implementer's verification command. Do not re-review the task; proceed to the quality gate and report any unresolved failures. |

If the reviewer flags something that's actually correct (compiles, tests pass, follows conventions), reject that specific feedback and proceed. Reviewers can be wrong — they lack full context.

### 1d. Task Fix Pass

Only run this step after `STATUS: CHANGES_REQUESTED`. Give the fixer the
reviewer handback and the existing brief/report paths. It may modify the
expected outputs to address the complete issue list, but it must not expand
scope. If the fixer returns `DONE`, proceed to the quality gate. If it returns
`BLOCKED`, stop the task and report the unresolved blocker; do not run the gate
or continue to another task unless the orchestrator or user explicitly chooses
to proceed. There is no second review cycle.

## Step 2: Quality Gate

Before the gate, resolve each command from the plan or task brief. If neither
specifies it, discover an established command from repository guidance and
configuration (for example, package scripts or build files). The orchestrator
must pass the resolved commands to the gate; do not invent commands. Record the
resolved command in the task handback.

After each task's lightweight review (and its optional task fix pass), run the
applicable checks from the project root. Then, after all tasks pass their gates,
run the final aggregate review described below.

1. **Build/compile** — the resolved build command must succeed
2. **Tests** — the resolved test command must pass
3. **Lint** — the resolved lint command must be clean

If the plan or repository establishes that a gate is not applicable, record it
as `not applicable` with the reason. If an applicable command cannot be supplied
or discovered, record that gate as `unavailable` with the missing-command reason;
do not treat it as passed. If any gate fails, or is unavailable, record the
unresolved verification result in the task handback and continue only if the
orchestrator or user explicitly chooses to proceed. Do not automatically
dispatch another fix or review loop. Once all applicable gates pass, continue
to the next task. Do not treat the lightweight task review as the final quality
review.

## Step 3: Final Aggregate Code Review

After all tasks and their quality gates pass, generate an aggregate diff from
the implementation baseline. Include every task's changed file and the final
plan/feature requirements, not only the last task's diff. If the implementation
was not committed, use `git diff` against the baseline; if it was committed,
use the commits produced by the implementation cycle. Write the result to
`.agents/plans/review-final.diff`. Use
`references/final_reviewer_prompt.md` and dispatch one fresh reviewer. That
reviewer must apply the full `code-review` skill and inspect the feature
end-to-end.

Pass the plan path, all implementation report paths, and the aggregate diff
path into the final reviewer template. Do not pass only the last task's brief
or report.

If the final reviewer returns `STATUS: PASSED`, the plan is complete. If it
returns `STATUS: CHANGES_REQUESTED`, dispatch one final consolidated fix pass
with all critical, high, and medium findings (and practical low findings).
Read `references/final_fixer_prompt.md` and provide the plan path, all report
paths, aggregate diff path, complete reviewer handback, resolved verification
commands, and expected output paths. If the final fixer returns `STATUS: OK`,
run the applicable quality gates again. If it returns `STATUS: BLOCKED`, stop
and report the unresolved blocker; do not run the gate or continue unless the
orchestrator or user explicitly chooses to proceed. Do not dispatch another
reviewer or automatic fix loop. Report any unresolved verification failures.

## Context Discipline

- **Pass artifacts as file paths, not pasted content.** Subagents read brief, diff, and report files directly. Never paste full specs or diffs into dispatch prompts.
- **Read only verdicts from subagent outputs.** You want the reviewer `STATUS`, the implementer `DONE`/`BLOCKED`, and the issue list, not the full analysis.
- **Don't accumulate state.** After a task is approved, drop its details. Only carry forward interfaces the next task needs.
- **At ~70%+ context:** checkpoint completed tasks, finish the current one, and warn the user.
