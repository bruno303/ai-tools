```skill
---
name: testing-guidelines
description: Defines testing strategy, structure, and standards for Go projects.
---

## 1. Test Priority

1. **Unit tests** — mandatory for all business logic (entities, services, use-cases).
2. **Integration tests** — required for happy paths and common alternative paths of services/use-cases.
3. **End-to-end tests** — out of scope unless explicitly requested.

## 2. Unit Test Rules
- Every exported function, method, and constructor must have at least one unit test.
- Unit tests must be **fully isolated**: no real databases, no real HTTP calls, no real message brokers.
- **Always mock external dependencies** using a mock library. Preferred order:
  1. `testify/mock` (if already used in the project).
  2. `gomock` (if already used in the project).
  3. `testify/mock` (default for new projects).
- Tests live in `_test.go` files alongside the source file (same package or `_test` package for black-box tests).
- Test both the **success path** and all **meaningful error/edge-case paths**.

## 3. Integration Test Rules
- Cover the **happy path** and **common alternative paths** (e.g., not found, conflict, timeout).
- Infrastructure lifecycle is managed externally via **Make commands**, not from within test code:
  - Bring infrastructure up with `make infra-up` (which runs `docker compose up -d`).
  - Tear it down with `make infra-down` (which runs `docker compose down`).
  - Never use `testcontainers-go`, `dockertest`, or any library that manages container lifecycle from inside tests — they cause connection and lifecycle issues.
- Read connection strings from **environment variables** only (set by the compose environment or a `.env.test` file). Never hardcode addresses or credentials.
- Use `httptest.Server` for mocking HTTP dependencies that don't need a real container.
- Isolate integration tests with the `//go:build integration` build tag so they are excluded from the default `go test ./...` run.
- File naming: `<name>_integration_test.go` or files under an `integration/` subdirectory.

## 4. Test Naming Convention
Use the pattern: `Test<Function>_<Condition>_<ExpectedOutcome>`

Examples:
- `TestNewOrder_WhenItemsIsEmpty_ReturnsError`
- `TestCreateOrderService_HappyPath_PersistsAndReturnsOrder`
- `TestGetUser_WhenNotFound_ReturnsNotFoundError`

## 5. What NOT to Test
- Trivial getters/setters with no logic.
- Auto-generated code (protobuf, ORM models).
- Framework wiring (router setup, DI container boot).

## 6. Verification
- All tests must be **green before handback**. Never commit failing tests.
- Run `go test ./...` for unit tests.
- Run `go test -tags=integration ./...` for integration tests.
```
