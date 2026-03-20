---
name: architectural-guidelines
description: Enforces Clean Architecture principles and layer responsibility rules across projects.
---

## 1. Core Philosophy
- **Separation of Concerns**: Keep Business Logic (Domain/Usecase) strictly separated from Infrastructure (DB, API, External Services).
- Prefer interfaces for dependencies to allow mocking and testing.

## 2. Layer Responsibilities

### Entity Layer
- Entities own their own **invariants and validation rules**. Any rule intrinsic to an object (e.g., "an Order must have at least one item", "an email must be valid") must be implemented as a method on the entity itself.
- Entities must be **self-protecting**: construction via factory functions should enforce mandatory invariants and return an error if violated.
- Entities must **never import** repositories, services, or any infrastructure package.

### Service / Use-Case Layer
- Services are responsible for **orchestrating the business flow**: coordinating entities, calling repositories, dispatching events, and enforcing rules that span multiple aggregates or require external data.
- Services must **delegate entity-level rules to the entity**. A service must never re-implement validation that already belongs in an entity method.
- Services must **never import infrastructure** directly. They must depend only on repository/gateway **interfaces** defined in the domain.

### Cross-Layer Constraints
- **No rule leakage downward**: Infrastructure and framework code must not contain business logic.
- **No rule leakage upward**: Entity-intrinsic rules must not be scattered across services, handlers, or middleware.
- **Repositories are interfaces**: Concrete implementations live in the infrastructure layer. The domain layer only sees the interface.

## 3. Decision Framework: Where Does This Logic Belong?

When implementing new behavior, use this reasoning process:

### Step 1: Is this a data integrity or field-level rule?
**→ Entity Layer**
- Rules that validate the *state* of a single object: field formats, mandatory fields, value ranges, relationship constraints within the entity
- Examples: `Email` must be valid format, `Order` must have at least one item, `Price` cannot be negative

### Step 2: Does this rule depend on external data or cross-aggregate coordination?
**→ Service/Use-Case Layer**
- Rules that require fetching data from repositories, calling other services, or coordinating multiple entities
- Examples: "check if email is unique across all users", "transfer funds between two accounts", "apply discount based on loyalty tier"

### Step 3: Is this business flow orchestration?
**→ Service/Use-Case Layer**
- Multi-step business processes that coordinate entities, repositories, and events
- Examples: "create order → reserve inventory → charge payment → send confirmation"

### Step 4: Is this infrastructure interaction?
**→ Infrastructure Layer**
- Database queries, HTTP calls, message publishing, file I/O
- Examples: repository implementations, API clients, event publishers

### Step 5: Is this presentation/transformation logic?
**→ DTO Layer**
- Converting domain objects to API responses, formatting data for clients
- Examples: response mapping, pagination formatting

### Quick Reference Table

| Logic Type | Layer | Example |
|------------|-------|---------|
| Field validation (format, required, range) | Entity | `ValidateEmail()` |
| Cross-aggregate rules | Service | `TransferFunds()` |
| Repository operations | Infrastructure | `PostgresOrderRepo.FindByID()` |
| Response formatting | DTO | `ToOrderResponse()` |
| Business orchestration | Service | `CreateOrderUseCase()` |

## 4. Data Transfer
- Never expose Database Entities/Models directly to the API.
- Always map to a DTO/Response struct before returning to the customer.

## 5. Onboarding Protocol (Agent Task)
- Before writing any code, the agent MUST:
  1. Scan the existing directory structure.
  2. Identify the "Source of Truth" for existing patterns (e.g., look at an existing Service).
  3. Propose the file location to the user and explain how it fits the architecture.
