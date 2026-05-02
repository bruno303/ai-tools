---
name: write-tests
description: Use when writing or updating tests for changed behavior, including choosing the right test level and covering the main success and failure paths.
---

# When to use
Use for:
- new behavior
- bug fixes that need regression coverage
- refactors where behavior must remain unchanged

Do not use for:
- broad architecture review
- exploratory debugging before the target behavior is clear

# Goal
Add or update the narrowest useful tests that prove the intended behavior.

# Process
1. Identify the public behavior that changed.
2. Choose the appropriate test level.
3. Follow existing test patterns in the repository.
4. Cover the happy path, main failure path, and one edge case when relevant.
5. Keep fixtures and mocks minimal.

# Rules
- Prefer behavior-focused assertions over implementation-detail assertions.
- Mock only true boundaries.
- Reuse helpers and fixtures already present in the repo.
- Avoid expanding scope into unrelated test cleanup.

# Output
Provide:
- test files added or changed
- behaviors covered
- any remaining important gaps
