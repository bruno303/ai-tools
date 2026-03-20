---
name: go-testing-guidelines
description: Go-specific testing strategy, conventions, and standards.
---

## 1. Mock Libraries
Prefer the project's existing mock strategy. Preferred order:
1. `testify/mock` (if already used in the project).
2. `gomock` (if already used in the project).
3. `testify/mock` (default for new projects).

## 2. File Conventions
- Tests live in `_test.go` files alongside the source file (same package or `_test` package for black-box tests).
- Isolate integration tests with the `//go:build integration` build tag so they are excluded from the default `go test ./...` run.
- File naming: Integration tests must be files under an `integration/` subdirectory.

## 3. Integration Infrastructure
- Never use `testcontainers-go`, `dockertest`, or any library that manages container lifecycle from inside tests — they cause connection and lifecycle issues.
- Use `make infra-up` / `make infra-down` for container lifecycle (which runs `docker compose up -d` / `docker compose down`).
- Read connection strings from environment variables only (set by the compose environment or a `.env.test` file). Never hardcode addresses or credentials.
- Use `httptest.Server` for mocking HTTP dependencies that don't need a real container.

## 4. Test Naming Convention
Use the pattern: `Test<Function>_<Condition>_<ExpectedOutcome>`

Examples:
- `TestNewOrder_WhenItemsIsEmpty_ReturnsError`
- `TestCreateOrderService_HappyPath_PersistsAndReturnsOrder`
- `TestGetUser_WhenNotFound_ReturnsNotFoundError`

## 5. Verification
- Run `go test ./...` for unit tests.
- Run `go test -tags=integration ./...` for integration tests.
- If the project contains make commands for tests, prioritize using those (e.g., `make test-unit`, `make test-integration`) as they may include additional setup or flags.
