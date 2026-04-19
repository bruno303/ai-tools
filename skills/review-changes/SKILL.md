---
name: review-changes
description: Use after implementation to review changes for correctness, architecture fit, edge cases, regressions, and missing tests.
---

# When to use
Use for:
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
4. Look for missed failure paths, edge cases, and contract breaks.
5. Check whether tests cover the important behavior.

# Rules
- Prioritize correctness and regressions over style.
- Report findings by severity.
- Be specific about the affected file, risk, and recommended fix.
- Do not invent issues without grounding in the code or task.

# Output
Provide findings grouped as:
- critical
- medium
- low
- missing tests or follow-ups

If no meaningful issues are found, say so explicitly.
