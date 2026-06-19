---
name: subagent-plan-execution
description: Execute an existing implementation plan by dispatching fresh subagents per task, with mandatory spec-compliance and code-quality review gates. Only use this skill when explicitly invoked via /subagent-plan-execution — do NOT trigger automatically based on context or user phrasing.
---

# Subagent-Driven Plan Execution

## Why this works

Each task gets its own fresh subagent with zero accumulated state. You, the orchestrator, stay lean — routing work and checking verdicts rather than absorbing diffs, debug logs, and intermediate code. Two mandatory review gates (spec compliance, then code quality) catch problems task-by-task before they compound into rework across the whole plan.

This is the discipline that makes multi-task implementations tractable at quality. Skipping any gate is how you end up with a "working" feature that violates the spec in subtle ways or a codebase full of inconsistencies you only discover at the end.

## Step 0: Parse the plan and set up

Check for an existing progress ledger first:

```
cat .agents/plans/progress.md
```

If it exists, tasks listed as complete are **DONE** — do not re-dispatch them. Resume at the first task not marked complete. The ledger survives context compaction; trust it and `git log` over your own recollection.

If no ledger exists, read the plan file (or extract tasks from conversation context) **once**, upfront. Build an internal task list. Then close the plan — don't keep re-reading it, and don't make subagents read the whole plan. Create `.agents/plans/` if it doesn't exist.

Track progress with whatever task mechanism your platform provides (see Platform Mechanics), **and** maintain the `.agents/plans/progress.md` ledger as a recovery map.

## Step 1: Implement

Before dispatching, record the current HEAD commit — you'll need it for the review package:

```
BASE=$(git rev-parse HEAD)
```

Write the task spec to a brief file so it never gets pasted through your context:

```
# On platforms with bash:
mkdir -p .agents/plans
cat > .agents/plans/task-N-brief.md << 'EOF'
<full task spec verbatim from the plan>
EOF

# On platforms without bash:
Write the task text to .agents/plans/task-N-brief.md using your Write tool
```

Spawn a fresh implementer subagent. Include in its prompt:

- **The brief file path** — tell it to read `.agents/plans/task-N-brief.md` first; that file is its requirements
- **Project context**: language, framework, key conventions, where tests live, how to run them
- **Expected outputs**: specific files, function signatures, test coverage required
- **Verification command**: the exact command to confirm it works before finishing
- **Report file path**: `.agents/plans/task-N-report.md` — the implementer writes its full report there and returns only a short summary
- **Commit instructions**: format and scope, if the plan requires commits per task

One task, one subagent. Don't bundle adjacent tasks into one call — you lose the clean review boundary.

## Handling implementer status

The implementer reports one of four statuses:

**DONE:** Proceed to spec compliance review (Step 2).

**DONE_WITH_CONCERNS:** Read the concerns before proceeding. If they're about correctness or scope, address them before review. If they're observations (e.g., "this file is getting large"), note them and proceed to review.

**NEEDS_CONTEXT:** The implementer needs information that wasn't provided. Supply it and re-dispatch.

**BLOCKED:** The implementer cannot complete the task. Assess:
1. If it's a context problem → provide more context and re-dispatch
2. If the task requires more reasoning → re-dispatch with a more capable model
3. If the task is too large → split it and re-dispatch the smaller pieces
4. If the plan itself is wrong → escalate to the user

Never ignore a BLOCKED status or retry without changing something.

## Step 2: Spec compliance review (mandatory gate 1)

Generate a review package — a single file containing the commit list, stat summary, and full diff — so the reviewer reads one file rather than deriving the diff itself:

```
# On platforms with bash:
git log --oneline $BASE..HEAD > .agents/plans/review-task-N.diff
git diff --stat $BASE..HEAD >> .agents/plans/review-task-N.diff
git diff -U10 $BASE..HEAD >> .agents/plans/review-task-N.diff

# On platforms without bash:
Gather git log --oneline, git diff --stat, and git diff -U10 for the range,
then write it all to .agents/plans/review-task-N.diff using your Write tool.
Use the BASE you recorded before dispatching the implementer — never HEAD~1,
which silently truncates multi-commit tasks.
```

Spawn a fresh reviewer subagent. Give it:

- The **brief file path** (`.agents/plans/task-N-brief.md`) — not the spec pasted inline
- The **report file path** (`.agents/plans/task-N-report.md`) — the implementer's claims to verify against
- The **review package path** (`.agents/plans/review-task-N.diff`)
- Instructions to verify: every requirement implemented, file paths match, signatures match, no scope creep, nothing missing

The reviewer must output:
- `✅ Spec compliant` or `❌ Issues found` with specific gaps
- `⚠️ Cannot verify from diff` for any requirement that lives in unchanged code or spans tasks — these don't block the verdict, but **you** must resolve each one before marking the task complete (you hold the cross-task context the reviewer lacks)

**If gaps are found:** spawn a fix subagent with the gap list. Re-run spec review with a fresh review package. Repeat until `✅`. There is no "close enough" — a partial spec is a failed spec.

Do not move to quality review until spec compliance is `✅`.

## Step 3: Code quality review (mandatory gate 2)

Only after spec `✅`. Spawn a fresh quality reviewer with the same three file paths (brief, report, review package) and instructions to assess: project conventions, error handling, naming, test coverage, edge cases, security, no obvious bugs.

It must output `APPROVED` or tiered issues:
- **Critical**: must fix before proceeding
- **Important**: must fix before proceeding
- **Minor**: optional, note but don't block

**If Critical or Important issues exist:** spawn a fix subagent, generate a new review package (updated BASE..HEAD), re-run quality review. Repeat until `APPROVED`. Minor issues can be deferred but must be logged in the progress ledger.

## Step 4: Mark complete, continue

Once both gates pass, append one line to the ledger:

```
Task N: complete (commits <base7>..<head7>, review clean)
```

Also mark the task complete in your platform's task tracker. Keep only the verdicts in your working context — not the full diffs or reviewer outputs. Then start Step 1 for the next task.

**Execute tasks continuously.** Do not pause between tasks to ask "should I continue?" — the user asked you to execute the plan, so execute it. The only reasons to stop are: a BLOCKED status you cannot resolve, ambiguity that genuinely prevents progress, or all tasks complete.

## Step 5: Final integration check

After all tasks are complete, spawn one integration reviewer. Give it:

- All files changed across the full plan (pass paths, not inlined content)
- A brief description of each task's intent
- Instructions to check: components fit together, no cross-task inconsistencies, all tests pass end-to-end

Run the full test suite yourself (or via subagent) and confirm green. Only then is the plan complete.

---

## Platform Mechanics

Use whatever subagent spawning and task tracking your platform provides:

| Platform | Spawn subagent | Task tracking |
|---|---|---|
| **Claude Code** | `Agent` tool | `TaskCreate` / `TaskUpdate`, or a markdown checklist in a temp file |
| **Hermes Agent** | `delegate_task` | `todo()` |
| **OpenCode** | Agent spawn command (platform docs) | Internal notes or a file-based checklist |
| **No subagent support** | Execute tasks in your current context | Warn the user that context will accumulate; quality may degrade on large plans |

If no subagent mechanism is available, execute inline but be explicit with the user: "I don't have a way to spawn fresh subagents here, so I'll run this in-context. Quality on large plans may be lower than with subagent delegation."

---

## Context discipline (orchestrator rules)

The orchestrator routes — it doesn't accumulate.

- **Pass artifacts as files, not pasted text.** Task specs go into brief files; diffs go into review packages; implementer reports go into report files. Everything you paste into a dispatch prompt stays resident in your context for the rest of the session. Keep prompts to: (1) where the task fits in the project; (2) the brief file path; (3) interfaces from earlier tasks the brief can't know; (4) the report file path. Exact values and specs live only in the brief.
- **Read subagent outputs at summary depth.** You want the verdict (PASS / APPROVED / issue list), not the full content.
- **Never inline large file contents into subagent prompts.** Pass the path; let the subagent read it.
- **Do not paste accumulated prior-task summaries into later dispatches.** A fresh subagent needs its task, the interfaces it touches, and the global constraints — nothing else.
- **Delegate any heavy analysis** to a subagent — don't do it in your own context.
- **At ~50% context capacity:** warn the user, checkpoint which tasks are complete, and consider whether to continue or hand off to a fresh session.
- **At ~70%+ context capacity:** checkpoint immediately. Finish the current task cleanly, surface your progress, and stop.

---

## Task sizing

Right-sized tasks = 2–5 minutes of focused work, touching 1–3 files, describable in a short paragraph. If a task's spec takes more than a paragraph or touches many files, split it before starting execution.

---

## Handling issues during execution

**Subagent asks a clarifying question:** Answer completely before letting them proceed. Don't rush — an underspecified implementation will fail review.

**Subagent fails or produces broken output:** Spawn a new fix subagent with a specific description of what went wrong. Don't attempt the fix in orchestrator context.

**Review finds issues:** Fix via subagent, generate a new review package, re-run the same review gate. Never skip re-review after a fix — the fix itself might introduce a new issue.

**Reviewer flags ⚠️ "cannot verify from diff":** Resolve each one yourself before marking the task complete. If you find a real gap, treat it as a failed spec review and send it back.

**Cascading failures (multiple tasks failing):** Pause, checkpoint what's complete, surface the pattern to the user. The plan spec may need revision before continuing.

---

## Constructing reviewer prompts

- Do not pre-judge findings for the reviewer. Never instruct a reviewer to ignore or not flag a specific issue. If a prompt you are writing contains "do not flag," "don't treat X as a defect," or "the plan chose" — stop: you are pre-judging. Let the reviewer raise it and adjudicate in the review loop.
- The global constraints you hand the reviewer are its attention lens. Copy binding requirements verbatim from the plan's Global Constraints section: exact values, exact formats, stated relationships between components. Process rules are already implied by the review gate — the constraints block is for what THIS plan demands.
- Do not ask a reviewer to re-run tests the implementer already ran on the same code. The implementer's report carries the test evidence.

---

## What not to do

- Start spec review before the implementer says it's done and verified
- Start quality review before spec compliance is `✅`
- Proceed to the next task while any Critical or Important quality issues are open
- Let the implementer self-review replace the review gates — self-review is not a gate
- Accumulate full diffs, file contents, or reviewer analyses in orchestrator context
- Declare the plan done without running the final integration check
- Re-dispatch a task the progress ledger already marks complete — check the ledger after any compaction or resume
