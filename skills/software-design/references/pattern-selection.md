# Pattern Selection

Start from the problem, not the pattern. Find the row that matches the concrete
force, then read the discriminator for the candidates that look similar.

If no row fits, use the direct implementation. "No pattern" is a valid choice,
and it is often the best one.

## Problem-first table

| Force or symptom | Candidate patterns | Prefer first |
| --- | --- | --- |
| Multiple interchangeable algorithms selected at runtime | Strategy, State | Strategy; State only when transitions are central |
| Object behavior changes with lifecycle state | State, Strategy | State when legal transitions are central; otherwise a status field with guards |
| Add behavior around an object without changing its type | Decorator, Middleware | Decorator for object behavior; middleware for request pipelines |
| Cross-cutting request behavior | Middleware, Decorator | Middleware |
| Isolate domain code from persistence | Repository, Unit of Work | Repository; add Unit of Work when transaction scope matters |
| Multiple writes must succeed or fail together | Unit of Work, direct transaction | Unit of Work only when change tracking or aggregate coordination is real |
| Complex object construction with many optional parts | Factory, Builder | Factory for creation choice; Builder for stepwise construction and validation |
| Third-party API does not match the domain interface | Adapter | Adapter |
| Sequential processing with fallback or approval steps | Chain of Responsibility | Chain only when handlers genuinely vary and may stop the request |
| Decouple producer from multiple consumers | Observer / Events | Direct calls when there is only one consumer |
| Cross-cutting request behavior around one handler | Middleware | Middleware |
| Immutable domain concept with rules | Value Object | Value Object |
| Dependency wiring and lifecycle | Dependency Injection | Constructor or parameter injection |
| One shared resource with a process-wide lifecycle | Singleton, DI-managed instance | DI-managed single instance; Singleton only for a true global resource |
| No clear force or a single call site | No pattern | Direct implementation |

## Similar-pattern discriminators

### Strategy vs State

- **Strategy** is selected from outside and usually has no transition logic.
  Variants are interchangeable for the same call.
- **State** makes transitions part of the behavior. The object moves between
  states and legal moves are central.
- If state is a simple enum and transitions are trivial, use a status field with
  guard clauses instead of a type per state.

### Adapter vs Decorator vs Middleware

- **Adapter** changes the interface so an incompatible API fits the client.
- **Decorator** keeps the interface and adds behavior around one object.
- **Middleware** keeps the handler contract and applies behavior across a
  request pipeline.
- If only a method name or type differs at one local call site, translate inline
  instead of adding an adapter type.

### Repository vs direct data access

- **Repository** protects a domain/persistence boundary, aggregate access,
  replaceable storage, or domain tests that should not need a database.
- **Direct access** is fine for simple CRUD, one query shape, reporting and read
  models, or a project where the ORM is the established domain model.
- Do not put a repository over every table or turn it into a generic query
  builder.

### Factory vs Builder

- **Factory** chooses and creates a type; it hides which concrete type the caller
  receives.
- **Builder** assembles one complex object step by step and validates before
  returning it.
- For a few parameters, a plain constructor or options record is enough.

### Chain of Responsibility vs Middleware vs Observer

- **Chain** sends one request to one handler, possibly passing it along until
  handled. Handlers may stop the request.
- **Middleware** runs every layer around a handler for cross-cutting concerns.
- **Observer / Events** delivers one event to many independent consumers with no
  single handler.
- If the caller needs a deterministic result from exactly one handler, prefer a
  direct dispatch table or conditional over a chain.

### Singleton vs DI-managed instance

- **DI-managed single instance** is the default when one instance is needed but
  dependencies should stay explicit and testable.
- **Singleton** is only for a true process-wide resource with controlled
  initialization. Never use it as a service locator.
- If tests need to reset or replace the instance, DI is the better seam.

## Selection rules

- Prefer no pattern when direct code is clear and the change is local.
- Prefer the repository's existing pattern over a textbook alternative.
- Prefer composition over inheritance.
- Prefer the fewest concepts that resolve the force.
- Define the seam and its test before adding the abstraction.
- If two candidates are equal, choose the one that keeps call flow easier to
  follow.
- Record the rejected alternatives when the choice is material.
