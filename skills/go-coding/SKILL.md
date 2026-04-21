---
name: go-coding
description: Use when writing or reviewing Go code to ensure it follows common conventions for readability, maintainability, and correctness.
---

# When to use
Apply these Go conventions when reading, generating, or reviewing Go code.

# Function signatures
- Accept `context.Context` as the first parameter when the function need it
- Do not store `context.Context` in structs.
- Do not pass nil context; use `context.Background()` or `context.TODO()` at process edges.

# Errors
- Return errors explicitly.
- Wrap unexpected errors with `%w` to preserve the cause.
- Use sentinel errors only when callers need `errors.Is`.
- Prefer adding operation context to wrapped errors.
- Do not panic for runtime/business errors.
- Panics are acceptable for invalid startup wiring or impossible programmer errors in constructors.

# Interfaces
- Keep interfaces small and behavior-focused.
- Define interfaces close to the consuming code, not automatically near implementations.
- Add compile-time interface assertions:
  - `var _ MyInterface = (*MyType)(nil)`

# Constructors
- Use `NewX(...)` constructors for types that require dependencies or non-zero initialization.
- Validate required dependencies in constructors.
- Return concrete types from constructors unless callers truly need an interface.

# Receivers and types
- Use pointer receivers for:
  - mutable state
  - types containing mutexes/atomics
  - large structs
- Use value receivers only for small, copy-safe structs with immutable-like behavior.
- Prefer concrete structs plus methods over premature interfaces.

# Context and timeouts
- Propagate context through all layers.
- Use `context.WithTimeout` for bounded external operations and cleanup paths.
- Cancel derived contexts with `defer cancel()`.
- Respect `ctx.Done()` in retry loops and long-running operations.

# Concurrency
- Protect shared mutable state with the right sync primitive:
  - `sync.Mutex` / `sync.RWMutex` for guarded state
  - `sync.Once` for idempotent close/init
  - `atomic` for simple flags/counters
  - `sync.Map` only when its tradeoffs fit
- Keep critical sections small.
- Document non-obvious synchronization requirements.

# Resource lifecycle
- Close resources deterministically.
- Place `defer` immediately after successful acquisition when practical.
- Make shutdown/close idempotent when the type owns long-lived resources.

# Logging and observability
- Pass context into logs when logger supports it.
- Keep observability setup at application edges.
- Prefer wrappers/decorators/middleware for tracing and metrics over polluting business logic.

# API design
- Keep exported APIs minimal.
- Prefer explicit input/output structs when function arguments are growing or likely to evolve.
- Keep transport/request DTOs separate from domain/internal models.

# Testing
- Unit test behavior, not implementation details.
- Mock only true boundaries.
- Use interface assertions in tests or production code for contract safety.
- Cover success, dependency failure, and sentinel-error paths.

# General Go style
- Keep packages cohesive.
- Keep files centered around one concept.
- Prefer straightforward control flow.
- Avoid hidden magic and unnecessary abstraction.
- Use the standard library first unless a dependency clearly improves the code.
- Prefer early returns and guard clauses to reduce nesting.
- Avoid unnecessary `else` after returns.
- Use naked returns only in very small functions.
