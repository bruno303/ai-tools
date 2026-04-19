---
name: debug-failure
description: Use when tests, builds, CI, or runtime behavior fail and the task is to isolate the root cause and propose the smallest reliable fix.
---

# When to use
Use for:
- failing tests or builds
- runtime errors or unexpected behavior
- CI failures or flaky behavior requiring triage

Do not use for:
- feature planning without a concrete failure
- broad code review unrelated to a specific problem

# Goal
Move from symptom to probable root cause with a grounded minimal fix and regression protection.

# Process
1. Capture the exact failure signal.
2. Identify the affected component, layer, or boundary.
3. Separate symptom, trigger, and likely root cause.
4. Narrow the failing surface with the smallest reproduction possible.
5. Propose the smallest reliable fix.
6. Recommend or add regression verification.

# Rules
- Preserve exact error messages and important logs.
- Distinguish confirmed facts from hypotheses.
- Avoid speculative rewrites.
- Prefer fixes that reduce risk and clarify behavior.

# Output
Provide:
- observed failure
- likely root cause
- affected files or components
- proposed fix
- verification or regression test recommendation
