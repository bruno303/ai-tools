---
name: architectural-guidelines
description: Enforces Clean Architecture principles and layer responsibility rules across projects.
---

## 1. Core Philosophy
- **Separation of Concerns**: Business logic MUST remain strictly separated from infrastructure concerns such as databases, APIs, frameworks, and external services.
- Dependencies SHOULD be expressed through interfaces or equivalent contracts when doing so improves substitution, testing, or architectural clarity.
- Responsibility-based placement MUST take priority over naming. Folder and package names MAY vary by project, but ownership rules MUST remain consistent.

## 2. Dependency Direction
- **Domain** MUST NOT import application/use-case, infrastructure, delivery, or framework packages.
- **Application / Use-Case** MAY depend on domain types and domain-owned interfaces, but MUST NOT import infrastructure or framework code.
- **Infrastructure** MAY depend on domain and application contracts to implement them, but MUST NOT own business rules.
- **Delivery / Transport** MAY depend on application/use-case entry points and DTOs, but MUST NOT contain business logic.
- If a project uses different names for these layers, agents MUST preserve the existing naming while keeping the same dependency direction.

## 3. Layer Responsibilities

### Entity Layer
- Entities MUST own their own invariants and validation rules. Any rule intrinsic to a single object MUST be implemented on the entity or value object itself.
- Entities MUST be self-protecting. Construction through factories or equivalent constructors MUST enforce mandatory invariants and return an error when violated.
- Entities and value objects MUST NOT import repositories, services, framework code, or infrastructure packages.
- Value objects MUST encapsulate their own validation, normalization, and comparison behavior.
- Entities SHOULD expose behavior that preserves invariants and SHOULD avoid anemic models that push intrinsic rules outward.

### Service / Use-Case Layer
- Services and use cases MUST orchestrate business flows: coordinating entities, calling repositories, dispatching events, and enforcing rules that span multiple aggregates or require external data.
- Services and use cases MUST delegate entity-level rules to entities or value objects. They MUST NOT re-implement validation that already belongs there.
- Services and use cases MUST NOT import infrastructure directly. They MUST depend on repository or gateway interfaces owned closer to the business layer.
- Services and use cases MUST own transaction boundaries or unit-of-work coordination when a business operation spans multiple writes.
- Services and use cases MAY perform authorization and policy checks when those checks require external context, actors, roles, or cross-aggregate data.

### Cross-Layer Constraints
- Infrastructure and framework code MUST NOT contain business logic.
- Entity-intrinsic rules MUST NOT be scattered across services, handlers, middleware, or adapters.
- Repository abstractions MUST be visible to the business layer; concrete implementations MUST live in infrastructure.
- Repositories SHOULD return domain entities, value objects, or application-facing projections, and MUST NOT leak ORM or database models into business logic.
- Domain events MUST describe business facts. Integration events and transport concerns MUST be handled in infrastructure or delivery adapters.

## 4. Decision Framework: Where Does This Logic Belong?

When implementing new behavior, agents SHOULD use this reasoning process:

### Step 1: Is this a data integrity or field-level rule?
**→ Entity Layer**
- Rules that validate the *state* of a single object: field formats, mandatory fields, value ranges, relationship constraints within the entity
- Examples: `Email` must be valid format, `Order` must have at least one item, `Price` cannot be negative

### Step 2: Does this rule depend on external data or cross-aggregate coordination?
**→ Service/Use-Case Layer**
- Rules that require fetching data from repositories, calling other services, or coordinating multiple entities
- Examples: "check if email is unique across all users", "transfer funds between two accounts", "apply discount based on loyalty tier"

### Step 2a: Is this an authorization or policy decision?
**→ Usually Service/Use-Case Layer**
- If the rule depends on the acting user, roles, tenant membership, or external state, keep it in the service/use-case layer.
- If the rule is intrinsic to the entity state itself, keep it on the entity.
- Examples: "only account owners can close the account", "only managers can approve refunds over limit"

### Step 3: Is this business flow orchestration?
**→ Service/Use-Case Layer**
- Multi-step business processes that coordinate entities, repositories, and events
- Examples: "create order → reserve inventory → charge payment → send confirmation"

### Step 3a: Does this need a transaction, clock, ID generator, feature flag, or config lookup?
**→ Service/Use-Case Layer with injected dependencies**
- The decision to use them belongs to the use case; the concrete implementations belong to infrastructure.
- Examples: generating order IDs, reading current time, checking rollout flags, wrapping multi-repository writes in a transaction

### Step 4: Is this infrastructure interaction?
**→ Infrastructure Layer**
- Database queries, HTTP calls, message publishing, file I/O
- Examples: repository implementations, API clients, event publishers

### Step 4a: Is this caching?
**→ Infrastructure by default**
- Cache access is an infrastructure concern unless cache semantics are part of an explicit application policy.
- Do not hide business rules inside cache population logic.

### Step 5: Is this presentation/transformation logic?
**→ Delivery / DTO Mapping**
- Converting domain objects to API responses, formatting data for clients
- Examples: response mapping, pagination formatting

### Quick Reference Table

| Logic Type | Layer | Example |
|------------|-------|---------|
| Field validation (format, required, range) | Entity | `ValidateEmail()` |
| Authorization with actor/context | Service | `ApproveRefund(actor, refundID)` |
| Cross-aggregate rules | Service | `TransferFunds()` |
| Repository operations | Infrastructure | `PostgresOrderRepo.FindByID()` |
| Response formatting | Delivery / DTO Mapping | `ToOrderResponse()` |
| Business orchestration | Service | `CreateOrderUseCase()` |
| Time/ID/flags via abstractions | Service + Infra impl | `Clock`, `IDGenerator` |

## 5. Data Transfer
- Database entities and persistence models MUST NOT be exposed directly to APIs.
- Domain outputs SHOULD be mapped to DTOs or response models before returning to clients.
- Request parsing and response shaping MUST belong to delivery or transport adapters, not to entities.

## 6. Repository and Interface Rules
- Repository or gateway interfaces MUST be defined in the layer that owns the business workflow, following the project's established pattern.
- Interfaces SHOULD remain small and use-case oriented. Agents MUST NOT create broad "god" repositories.
- Repository methods SHOULD speak in domain language, not persistence language.
- Pagination, query-builder, and database abstractions MUST NOT leak into domain entities.

## 7. Anti-Patterns to Avoid
- Agents MUST NOT validate entity invariants in handlers, controllers, or middleware when entities or value objects can enforce them directly.
- Agents MUST NOT place SQL or ORM filters that encode business policy inside repositories without a corresponding business-level abstraction.
- Agents MUST NOT return ORM models directly from repositories into business logic.
- Infrastructure retries, caching, and message formatting MUST NOT silently change business outcomes.
- The same rule MUST NOT be duplicated across a service and an entity.

## 8. Testing Guidance
- Entity and value object invariants MUST be tested directly with focused unit tests.
- Service and use-case orchestration SHOULD be tested with mocked or faked repositories, gateways, clocks, and event publishers.
- Infrastructure adapters SHOULD be tested against real integrations or contract-style fixtures where appropriate.
- When a bug is caused by logic placement, agents MUST add or update a test in the layer that should own the rule.

## 9. Onboarding Protocol (Agent Task)
- Before writing any code, the agent MUST scan the existing directory structure.
- The agent MUST identify the "Source of Truth" for existing patterns by inspecting 2-3 similar implementations.
- The agent MUST follow established naming and folder conventions when they do not violate the dependency rules above.
- The agent MUST choose the most consistent file location based on the existing codebase.
- The agent MUST ask the user about placement only when multiple valid patterns exist and the choice would materially affect the design.
