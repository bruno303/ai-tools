---
name: go-architectural-guidelines
description: Go-specific Clean Architecture rules, directory conventions, and design patterns.
---

## 1. Directory Structure
- Go application-private packages SHOULD live under `internal/`.
- Projects SHOULD use a structure that makes architectural boundaries obvious, such as:
  - `internal/domain` for entities, value objects, domain services, and domain errors
  - `internal/usecase` or `internal/application` for orchestration and business workflows
  - `internal/infrastructure` for database, cache, queue, file I/O, external APIs, clocks, and ID generators
  - `internal/delivery/http` (or similar) for handlers, request/response DTOs, and transport wiring
- Agents MUST preserve the existing project layout when it already expresses these boundaries clearly.

## 2. Dependency Direction
- `domain` MUST NOT import `usecase`, `infrastructure`, `delivery`, or framework packages.
- `usecase` MAY import `domain` and small consumer-owned interfaces, but MUST NOT import concrete infrastructure adapters.
- `infrastructure` MAY import `domain` or `usecase` contracts to implement them, but MUST NOT own business rules.
- `delivery` MAY import `usecase`, DTOs, and transport libraries, but MUST NOT contain business logic.
- Package cycles MUST be avoided. In Go, import graphs are architecture graphs.

## 3. Dependency Injection
- Dependencies SHOULD be injected through constructors, for example `func NewService(repo Repository) *Service`.
- Functional options MAY be used for complex configuration when they improve clarity.
- Dependencies MUST be wired at the application boundary, such as `main`, the composition root, or transport bootstrap, not inside business packages.

## 4. Entity Conventions
- Entities MUST enforce invariants through methods or constructors, for example `func (e *Entity) Validate() error`.
- Factory constructors SHOULD be used for self-protecting construction, for example `func NewOrder(...) (*Order, error)`.
- Entities and value objects MUST NOT import repositories, services, or infrastructure packages.
- Value objects MUST encapsulate their own validation and normalization.
- Intrinsic rules MUST remain close to the entity and MUST NOT be pushed into handlers or use cases.

## 5. Interface and Repository Rules
- Interfaces SHOULD remain small and behavior-oriented.
- Interfaces SHOULD be defined near the consumer when possible. Agents MUST NOT create broad shared interfaces prematurely.
- Repository interfaces SHOULD speak in domain terms and MUST return domain entities, value objects, or use-case-facing projections rather than ORM structs.
- Concrete database, cache, queue, and API clients MUST live in `infrastructure`.

## 6. Delivery / HTTP Rules
- Handlers MUST parse transport input, perform transport-level validation, call a use case, and map the result to a response DTO.
- `gin.Context`, `http.Request`, and framework-specific types MUST NOT cross into `domain` or `usecase` packages.
- Persistence models MUST NOT be exposed directly in API responses.

## 7. Error Handling
- Errors MUST be handled explicitly with `if err != nil`.
- Errors SHOULD be wrapped with context using `%w`, for example `fmt.Errorf("create order: %w", err)`.
- `errors.Is` and `errors.As` MUST be used for branching instead of string matching.
- Code MUST return errors and MUST NOT panic for expected business or infrastructure failures.
- Sentinel or typed domain errors SHOULD be introduced only when callers need to make a meaningful decision from them.

## 8. Go Conventions
- The standard library SHOULD be preferred unless a specific library is already established in the project.
- `context.Context` MUST be the first parameter for operations that cross process, I/O, or request boundaries.
- Packages SHOULD remain small and cohesive. Agents MUST avoid dumping unrelated logic into utility packages.
- Packages SHOULD export only what other packages truly need.
- Pointer and value receivers MUST be chosen deliberately, and method sets SHOULD remain consistent.

## 9. Verification
- `go test ./...` SHOULD be the default verification step.
- `go build ./...` MUST be run when changes affect compilation boundaries, wiring, or public package APIs.
- Project-specific linting SHOULD be run when present, for example `make lint` or `golangci-lint run`.

## 10. Onboarding Protocol (Agent Task)
- Before writing code, the agent MUST inspect the existing package structure and identify the "Source of Truth" for current patterns.
- The agent MUST read 2-3 similar implementations before choosing where new code belongs.
- The agent MUST follow the established package naming and layout unless doing so would violate the dependency rules above.
- If multiple package locations are valid and the choice would materially affect the design, the agent MUST ask one targeted question; otherwise the agent MUST choose the most consistent option and proceed.
