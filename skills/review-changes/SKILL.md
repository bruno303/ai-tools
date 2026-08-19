---
name: review-changes
description: Use after implementation to review changes for correctness, architecture fit, edge cases, regressions, and missing tests.
---

# When to use
Use for:
- pull requests and implementation diffs
- final review before presenting or merging changes
- reviewing another agent's implementation
- regression-focused inspection after a bug fix

Do not use for:
- initial codebase discovery
- open-ended architecture redesign

# Goal
Find the highest-value issues in the current changes with concise, actionable feedback.

# Process
1. Inspect the changed behavior and affected files.
2. Check correctness against the task requirements.
3. Review architecture fit, naming, and cohesion.
4. Check affected contracts and integrations for breaking changes.
5. Look for missed failure paths, edge cases, and regressions.
6. Check whether tests cover the important behavior and identify missing tests.

# Rules
- Prioritize correctness and regressions over style.
- Report findings by severity.
- Ground findings in evidence, with affected file and line references where available.
- Be specific about the affected file, risk, and recommended fix or follow-up.
- Do not invent issues without grounding in the code or task.
- Review only: do not implement fixes or perform broad redesign.

# Output
Provide findings grouped as:
- critical
- medium
- low
- missing tests or follow-ups

If no meaningful issues are found, say so explicitly.
