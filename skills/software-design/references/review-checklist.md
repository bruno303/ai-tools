# Design Review Checklist

Use this during planning, implementation, and code review. A "no" answer is not
automatically a defect; it identifies where to look for a concrete cost.

## Justification

- Does each abstraction protect a real boundary or remove real duplication?
- Is there a simpler direct implementation, or could the change be local?
- Is the pattern solving a named problem, or is it speculative?
- Was an existing repository pattern reused before introducing a new one?
- Is the new concept introduced in the smallest scope that resolves the force?
- Is the pattern named and applied consistently with the rest of the repository?

## Responsibilities and dependencies

- Are responsibilities cohesive without being fragmented?
- Is the dependency direction preserved?
- Are interfaces declared at the consumer boundary rather than the producer?
- Are dependencies passed explicitly, or hidden in globals, singletons, or a
  service locator?
- Is construction separated from use at a composition root?
- Does the design avoid duplicating the same concept behind multiple abstractions?

## Pattern-specific checks

### Repository and Unit of Work

- Does the repository protect a domain/persistence boundary, or does it merely
  mirror every query?
- Are domain types kept free of ORM and transport details?
- Is the transaction boundary explicit and owned by the right layer?
- Does the unit of work have a real multi-write or change-tracking requirement?
- Do repositories avoid committing independently when a unit of work owns the
  transaction?

### Events and observers

- Are there genuinely multiple independent consumers?
- Would a direct call be clearer for one consumer?
- Are ordering, duplication, retry, and failure semantics defined?
- Is publication atomic with the producer's transaction, or is an outbox needed?
- Is subscription lifecycle bounded to avoid leaks?

### Middleware and decorators

- Is the behavior truly cross-cutting, or is it business logic?
- Is the ordering explicit and documented where it matters?
- Does each layer preserve the handler or component contract?
- Can the layer short-circuit, and is that behavior intentional?
- Is the wrapper stack shallow enough to debug?

### Strategy, State, and Chain of Responsibility

- Is the variation real and selected at a clear point?
- For State, are legal transitions enforced in one place?
- For Chain, is it clear what happens when no handler accepts the request?
- Could a conditional or dispatch table be simpler?
- Does each variant or handler have tests through the shared contract?

### Factory and Builder

- Does creation choice actually vary, or is there one concrete type?
- Are construction details validated in one place?
- Does the builder return an immutable, valid result?
- Is the factory becoming a god object or a switch that changes for every type?

### Value Object

- Does the concept have invariants or behavior, or is it an anemic wrapper?
- Is it immutable?
- Is equality by value?
- Does construction prevent invalid states?

### Singleton and Dependency Injection

- Is a single process-wide instance a real requirement?
- Would a DI-managed instance be testable and explicit enough?
- Is the dependency graph wired at a composition root?
- Has a container or global accessor hidden the actual dependencies?
- Are lifetimes correct for the resource being shared?

## Tests

- Do tests cover behavior at the new seam?
- Can the implementation be substituted without unrelated infrastructure?
- Are failure, fallback, and lifecycle paths covered?
- Do tests assert observable behavior rather than the pattern's structure?
- Is the new abstraction exercised through the contract its consumers use?

## Review guidance

- Report only concrete risks: hidden coupling, incorrect substitution,
  duplicated rules, data loss, transaction bugs, unhandled failures, or
  maintenance cost with a realistic future trigger.
- Do not report a SOLID violation in the abstract.
- Do not recommend a pattern unless the change has a named force that warrants
  it.
- Do not flag a difference from a textbook pattern when the project's existing
  pattern is consistent and works.
- A clean design with no new abstraction is a valid outcome.
