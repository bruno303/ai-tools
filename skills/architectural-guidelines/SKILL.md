---
name: architectural-guidelines
description: Enforces Clean Architecture and project-specific design patterns.
---

## 1. Project Philosophy
- **Separation of Concerns**: Keep Business Logic (Domain/Usecase) strictly separated from Infrastructure (DB, API, External Services).
- **Go Pattern**: Use the "Internal" directory for private logic. Prefer interfaces for dependencies to allow mocking.
- **Kotlin Pattern**: Use Sealed Classes for state management and Result types for error handling.

## 2. Structural Rules
- **Infrastructure**: All external API calls must live in `internal/infrastructure/` (Go).
- **Domain**: Business rules must not import any framework-specific libraries (no `gin`).
- **Dependency Injection**: 
  - Go: Use constructor injection (e.g., `NewService(repo Repository)`).
- **Reuse First**: Reuse existing code whenever possible. Duplicate code only as a last resort, and explicitly inform the user when duplication is introduced. Small, local refactors to enable reuse are allowed. If a reuse-driven refactor is large, ask the user for permission before proceeding.

## 3. Layer Responsibilities (Clean Architecture Enforcement)

### Entity Layer (`internal/domain/entity/`)
- Entities own their own **invariants and validation rules**. Any rule that is intrinsic to an object (e.g., "an Order must have at least one item", "an email must be valid") must be implemented as a method on the entity itself (e.g., `func (o *Order) Validate() error`).
- Entities must be **self-protecting**: construction via factory functions (e.g., `NewOrder(...)`) should enforce mandatory invariants and return an error if they are violated.
- Entities must **never import** repositories, services, or any infrastructure package.

### Service / Use-Case Layer (`internal/domain/service/` or `internal/usecase/`)
- Services are responsible for **orchestrating the business flow**: coordinating entities, calling repositories, dispatching events, and enforcing rules that span multiple aggregates or require external data.
- Services must **delegate entity-level rules to the entity**. A service must never re-implement validation that already belongs in an entity method.
- Services must **never import infrastructure** directly. They must depend only on repository/gateway **interfaces** defined in the domain.

### Cross-Layer Constraints
- **No rule leakage downward**: Infrastructure and framework code must not contain business logic.
- **No rule leakage upward**: Entity-intrinsic rules must not be scattered across services, handlers, or middleware.
- **Repositories are interfaces**: Concrete implementations live in `internal/infrastructure/`. The domain layer only sees the interface.

## 4. Data Transfer
- Never expose Database Entities/Models directly to the API. 
- Always map to a DTO/Response struct before returning to the customer.

## 5. Onboarding Protocol (Agent Task)
- Before writing any code, the agent MUST:
  1. Scan the existing directory structure.
  2. Identify the "Source of Truth" for existing patterns (e.g., look at an existing Service).
  3. Propose the file location to the user and explain how it fits the architecture.
