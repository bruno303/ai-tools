---
name: go-testing-guidelines
description: Defines testing strategy, structure, and standards across projects.
---

## 1. Test Priority

1. **Unit tests** — mandatory for business logic, invariants, branching behavior, and bug fixes.
2. **Integration tests** — required for infrastructure adapters and important end-to-end business flows inside the service boundary.
3. **End-to-end tests** — out of scope unless explicitly requested.

## 2. Test Strategy by Layer
- **Domain / Entity / Value Object Layer**: invariants, validation, normalization, and domain behavior MUST be tested directly.
- **Service / Use-Case / Application**: orchestration, branching logic, transactions, authorization, and interactions with mocked or faked boundaries MUST be tested.
- **Infrastructure**: repositories, clients, queues, caches, and file-system adapters SHOULD be tested against real integrations or contract-style fixtures when relevant.
- **Delivery / Transport**: request parsing, response mapping, status codes, and transport-specific validation SHOULD be tested when the project treats these as meaningful behavior.

## 3. Unit Test Rules
- Unit tests MUST cover business logic, branching behavior, invariants, orchestration, and regressions.
- Dedicated tests SHOULD NOT be required for trivial wrappers, pass-through getters/setters, or generated code unless the project already follows that convention.
- Unit tests MUST be isolated from process boundaries: no real databases, no real HTTP calls, no real message brokers, and no real filesystem or network side effects.
- External boundaries MUST be replaced with mocks, fakes, or stubs using the project's existing approach.
- Real domain objects SHOULD be preferred over mocks when testing pure business logic.
- Tests SHOULD live alongside the source they verify unless the repository already uses a separate test layout.
- Tests MUST cover the success path and all meaningful error, edge, and regression paths.

## 4. Integration Test Rules
- Integration tests MUST cover the happy path and common alternative paths such as not found, conflict, or timeout.
- Infrastructure lifecycle SHOULD be managed externally via project tooling, for example `make infra-up` or `docker compose up`.
- In-test container orchestration MAY be used only when the repository already standardizes on it. Agents MUST NOT introduce a second integration-test lifecycle model casually.
- Connection strings MUST be read from environment variables only. Agents MUST NOT hardcode addresses or credentials.
- Integration tests SHOULD be isolated using the project's build-tag or separate-suite mechanism so they are excluded from the default test run.
- File naming SHOULD follow project conventions, such as `_integration_test` suffixes, `integration/` subdirectories, or build-tagged test files.

## 5. Determinism and Boundaries
- Time, randomness, ID generation, environment variables, and external responses MUST be controlled so tests remain deterministic.
- Shared state MUST be reset between tests, and tests MUST NOT depend on execution order.
- Tests SHOULD assert business outcomes and observable behavior rather than internal implementation details, unless the implementation detail is itself the contract.

## 6. Test Naming and Style
Use the pattern: `Test<Function>_<Condition>_<ExpectedOutcome>`

Examples:
- `TestNewOrder_WhenItemsIsEmpty_ReturnsError`
- `TestCreateOrderService_HappyPath_PersistsAndReturnsOrder`
- `TestGetUser_WhenNotFound_ReturnsNotFoundError`

- Table-driven tests SHOULD be preferred when they make repeated scenarios clearer, especially in Go codebases.
- Test names MUST be descriptive enough to explain the behavior being protected.
- Failure messages SHOULD make the broken behavior easy to identify quickly.

## 7. What NOT to Test
- Agents SHOULD NOT spend effort testing trivial getters/setters with no logic.
- Agents SHOULD NOT spend effort testing auto-generated code such as protobufs, ORM models, or scaffolding.
- Agents SHOULD NOT spend effort testing framework wiring such as router setup, DI container boot, or configuration parsing unless the repository treats that wiring as meaningful behavior.

## 8. Verification
- All tests MUST be green before handback. Agents MUST NOT commit or hand back knowingly failing tests.
- Agents SHOULD run the narrowest relevant test command first, then broader verification as needed.
- The project's default unit test command MUST be run for unit-test changes.
- The project's integration test command MUST be run when infrastructure adapters or integration flows are touched.
- For Go projects, `go test ./...` SHOULD be the default baseline, followed by tagged or separate integration suites as needed.

## 9. Onboarding Protocol (Agent Task)
- Before writing tests, the agent MUST inspect the repository's existing test structure, helpers, naming, and fixture patterns and identify the "Source of Truth" for current test conventions.
- The agent MUST read 2-3 similar tests before choosing naming, helpers, or fixture style.
- The agent MUST follow the project's established test style unless it conflicts with these rules.
- Each new test MUST be placed in the layer that owns the behavior being protected.
- If fixing a bug caused by misplaced logic, the agent MUST add or update a test in the layer where that rule should live.
