---
name: api-change-checklist
description: Use when creating or changing an API endpoint, handler, integration contract, or external service interface that affects request-response behavior.
---

# When to use
Use for:
- new endpoints
- request or response contract changes
- auth or validation changes
- integration contract changes between services

Do not use for:
- internal-only refactors with no contract effect
- pure database schema changes without API impact

# Goal
Force important API design details into the open before or during implementation.

# Clarification rule
Do not assume missing contract details. Ask the user targeted questions when important details are not specified.

# Checklist
Clarify or confirm when relevant:
- request fields, types, and optionality
- response shape and status codes
- authentication and authorization
- validation rules and error model
- idempotency behavior
- concurrency and race conditions
- pagination, filtering, and sorting
- retries, timeouts, and partial failure handling
- backward compatibility and versioning
- observability and audit requirements

# Rules
- Prefer explicit contracts over inferred behavior.
- Surface incompatibilities early.
- Keep changes compatible unless the task explicitly allows a breaking change.

# Output
Provide:
- confirmed contract details
- open questions
- compatibility risks
- implementation and test implications
