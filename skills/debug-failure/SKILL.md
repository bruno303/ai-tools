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
1. Capture the exact failure signal, including the command, inputs, environment, and relevant output.
2. Identify the affected component, layer, or boundary and trace backward through the call or data flow.
3. Compare the failing case with a working case or nearby implementation to identify the meaningful difference.
4. Separate confirmed facts from symptoms, triggers, and competing root-cause hypotheses.
5. Build the smallest tight reproduction that fails for the reported problem and use it as the feedback loop.
6. Test one hypothesis at a time with the smallest useful code or diagnostic change.
7. If the signal is insufficient, add temporary, focused instrumentation and remove it after diagnosis.
8. Propose the smallest reliable fix only after the root cause is supported by evidence.
9. Recommend or add regression verification, then run it freshly.

If three fix attempts fail, stop patching symptoms and question the relevant design, dependency, or architectural assumption before trying another implementation.

# Rules
- Preserve exact error messages and important logs.
- Distinguish confirmed facts from hypotheses.
- Do not propose a fix before completing enough evidence gathering to support a root-cause hypothesis.
- Prefer a tight, repeatable pass/fail signal over broad inspection or speculation.
- Avoid speculative rewrites.
- Prefer fixes that reduce risk and clarify behavior.

# Output
Provide:
- observed failure
- likely root cause
- affected files or components
- proposed fix
- verification or regression test recommendation
