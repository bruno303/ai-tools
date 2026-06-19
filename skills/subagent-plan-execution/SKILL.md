---
name: subagent-plan-execution
description: Execute an existing implementation plan by dispatching fresh subagents per task, with mandatory spec-compliance and code-quality review gates. Only use this skill when explicitly invoked via /subagent-plan-execution — do NOT trigger automatically based on context or user phrasing.
---

# Subagent-Driven Plan Execution

## Why this works

Each task gets its own fresh subagent with zero accumulated state. You, the orchestrator, stay lean — routing work and checking verdicts rather than absorbing diffs, debug logs, and intermediate code. Two mandatory review gates (spec compliance, then code quality) catch problems task-by-task before they compound into rework across the whole plan.

This is the discipline that makes multi-task implementations tractable at quality. Skipping any gate is how you end up with a "working" feature that violates the spec in subtle ways or a codebase full of inconsistencies you only discover at the end.

## Step 0: Parse the plan once

Read the plan file (or extract tasks from conversation context) **once**, upfront. Build an internal task list with the full text of each task. Then close the plan — don't keep reading it, and don't make subagents read it. You'll paste the relevant spec directly into each subagent's prompt.

Track progress with whatever task mechanism your platform provides (see Platform Mechanics). The goal is a clear record of what's done, what's in-flight, and what's pending.

## Step 1: Implement

Spawn a fresh implementer subagent per task. Include in its prompt:

- **The full task spec** from the plan, verbatim — not a paraphrase
- **Project context**: language, framework, key conventions, where tests live, how to run them
- **Expected outputs**: specific files, function signatures, test coverage required
- **Verification command**: the exact command to confirm it works before finishing
- **Commit instructions**: format and scope, if the plan requires commits per task

One task, one subagent. Don't bundle adjacent tasks into one call — you lose the clean review boundary.

## Step 2: Spec compliance review (mandatory gate 1)

Spawn a fresh reviewer subagent. Give it:

- The **original task spec** verbatim
- **File paths** of everything created or modified (let it read them — don't inline the content)
- Instructions to verify: every requirement implemented, file paths match, signatures match, no scope creep, nothing missing

It must output a clear `PASS` or a list of specific gaps.

**If gaps are found:** spawn a fix subagent with the gap list. Re-run spec review. Repeat until `PASS`. There is no "close enough" — a partial spec is a failed spec.

Do not move to quality review until spec compliance is `PASS`.

## Step 3: Code quality review (mandatory gate 2)

Only after spec `PASS`. Spawn a fresh quality reviewer. Give it:

- File paths to review (not inlined content)
- What to assess: project conventions, error handling, naming, test coverage, edge cases, security, no obvious bugs

It must output `APPROVED` or tiered issues:
- **Critical**: must fix before proceeding
- **Important**: must fix before proceeding  
- **Minor**: optional, note but don't block

**If Critical or Important issues exist:** spawn a fix subagent, re-run quality review. Repeat until `APPROVED`. Minor issues can be deferred but must be logged.

## Step 4: Mark complete, continue

Once both gates pass, mark the task complete in your tracker. Then start Step 1 for the next task. Keep only the verdicts in your working context — not the full diffs or reviewer outputs.

## Step 5: Final integration check

After all tasks are complete, spawn one integration reviewer. Give it:

- All files changed across the full plan
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

- **Read subagent outputs at summary depth.** You want the verdict (PASS / APPROVED / issue list), not the full content. If a reviewer writes a 200-line analysis, read the conclusion section.
- **Never inline large file contents into subagent prompts.** Pass the path; let the subagent read it.
- **Delegate any heavy analysis** to a subagent — don't do it in your own context.
- **At ~50% context capacity:** warn the user, checkpoint which tasks are complete, and consider whether to continue or hand off to a fresh session.
- **At ~70%+ context capacity:** checkpoint immediately. Finish the current task cleanly, surface your progress, and stop. Starting new tasks in a degraded context produces worse output than pausing.

---

## Task sizing

Right-sized tasks = 2–5 minutes of focused work, touching 1–3 files, describable in a short paragraph. If a task's spec takes more than a paragraph or touches many files, split it before starting execution.

---

## Handling issues during execution

**Subagent asks a clarifying question:** Answer completely before letting them proceed. Don't rush — an underspecified implementation will fail review.

**Subagent fails or produces broken output:** Spawn a new fix subagent with a specific description of what went wrong. Don't attempt the fix in orchestrator context.

**Review finds issues:** Fix via subagent, re-run the same review gate. Never skip re-review after a fix — the fix itself might introduce a new issue.

**Cascading failures (multiple tasks failing):** Pause, checkpoint what's complete, surface the pattern to the user. The plan spec may need revision before continuing.

---

## What not to do

- Start spec review before the implementer says it's done and verified
- Start quality review before spec compliance is `PASS`
- Proceed to the next task while any Critical or Important quality issues are open
- Let the implementer self-review replace the review gates — self-review is not a gate
- Accumulate full diffs, file contents, or reviewer analyses in orchestrator context
- Declare the plan done without running the final integration check
