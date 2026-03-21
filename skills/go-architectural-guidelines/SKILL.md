---
name: go-architectural-guidelines
description: Go-specific Clean Architecture rules, directory conventions, and design patterns.
---

## 1. Directory Structure
- **Infrastructure**: All external API calls must live in `internal/infrastructure/`.
- **Domain**: Business rules must not import any framework-specific libraries (no `gin`).
- Use the `internal/` directory pattern for private logic.

## 2. Dependency Injection
- Use constructor injection (e.g., `func NewService(repo Repository) *Service`).
- Prefer functional options for complex configuration.

## 3. Entity Conventions
- Implement invariants as methods: `func (e *Entity) Validate() error`.
- Use factory constructors for self-protecting construction: `func NewOrder(...) (*Order, error)`.
- Entities must never import repositories, services, or any infrastructure package.

## 4. Error Handling
- Strictly use `if err != nil` with context-aware error wrapping (`fmt.Errorf("operation: %w", err)`).
- Return errors, don't panic.

## 5. Standard Library
- Prefer standard library unless a specific library (like `zap` for logging) is already used in the project.

## 6. Verification
- Always run `make lint` or `go build ./...` before considering a task finished.
