# Package Layout and Architecture

Good Go architecture isn't about following a template — it's about keeping dependencies
flowing in one direction and making the codebase navigable.

## Package Design Principles

### Dependencies flow inward

```
handlers/boundaries → usecases → domain
     ↓                    ↓
infrastructure     infrastructure
(HTTP clients,     (databases,
 middleware)        message queues)
```

- **Domain** (models, business rules) depends on nothing external
- **Use cases** depend on domain interfaces, not concrete implementations
- **Boundaries** (HTTP handlers, Kafka consumers) depend on use cases
- **Infrastructure** (clients, repos) implements domain interfaces

This means:
- `domain/` never imports `infrastructure/` or `boundaries/`
- `usecases/` imports `domain/` interfaces, never concrete implementations
- `boundaries/` can import `usecases/` and `domain/`
- `infrastructure/` implements `domain/` interfaces

### Package naming

- Short, lowercase, singular nouns: `user`, `order`, `auth`, `payment`
- The package name is part of the API: `user.Service`, not `userservice.Service`
- Avoid stutter: `user.User` is fine; `user.UserService` is not — just `user.Service`
- Never name a package `util`, `helpers`, `common`, `misc`, or `base`

### What goes where

| Content | Location | Why |
|---------|----------|-----|
| Domain models (entities) | `domain/models/` or `internal/domain/` | Core business concepts, no external deps |
| Domain interfaces (ports) | `domain/clients/`, `domain/repos/` | Contracts that infrastructure implements |
| Use cases / services | `usecases/<feature>/` | Business logic orchestration |
| HTTP handlers | `boundaries/handlers/` or `boundaries/api/` | Request parsing, response writing |
| DTOs | `boundaries/dtos/` | Transport-layer data shapes |
| External clients | `infrastructure/clients/` | HTTP, gRPC, database implementations |
| Middleware | `boundaries/middlewares/` | Auth, logging, recovery, tracing |
| Config | `infrastructure/config/` | Configuration loading and validation |

### internal/ vs pkg/

- `internal/` — code that is private to this module. The Go compiler enforces this.
  Use for business logic, infrastructure, and anything not meant for external consumption.
- `pkg/` — code that *could* be imported by other projects. Only use if you genuinely
  have reusable library code. Most projects don't need `pkg/` at all.
- If in doubt, put it in `internal/`. You can always move it out later.

## Interface Ownership

Define interfaces where they are *consumed*, not where they are *implemented*.

```go
// domain/usecase.go — the consumer defines what it needs
package domain

type OrderRepository interface {
    FindByID(ctx context.Context, id string) (*Order, error)
    Save(ctx context.Context, order *Order) error
}

// infrastructure/postgres/order_repo.go — the implementation
package postgres

type OrderRepo struct {
    db *sql.DB
}

// Satisfies domain.OrderRepository without importing it
func (r *OrderRepo) FindByID(ctx context.Context, id string) (*domain.Order, error) {
    // ...
}
```

This keeps `infrastructure/` from importing `domain/` just for an interface,
and lets you swap implementations without touching business logic.

## Dependency Injection

Wire dependencies in a composition root — usually `main()` or a setup package.

```go
func main() {
    cfg := config.Load()
    db := postgres.Connect(cfg.Database)

    // Build from the inside out
    orderRepo := postgres.NewOrderRepo(db)
    paymentClient := stripe.NewClient(cfg.Stripe)

    orderService := order.NewService(orderRepo, paymentClient)

    handler := api.NewOrderHandler(orderService)
    router := api.NewRouter(handler)

    srv := &http.Server{Addr: cfg.Server.Addr, Handler: router}
    // ...
}
```

For larger codebases, a container pattern (dedicated setup packages that group
related dependencies) keeps `main()` manageable.

## When to Split a Package

Split when:
- A package has two groups of types that don't reference each other
- You need different test dependencies for different parts
- The package has grown past ~1000 lines and has distinct responsibilities

Don't split when:
- You'd create a package with only one type or function
- The split would create circular dependencies
- You're splitting just to match a "clean" directory structure

## File Organization Within a Package

```
usecases/createorder/
├── usecase.go        # Main business logic
├── usecase_test.go   # Tests
├── models.go         # Input/output types specific to this use case
└── errors.go         # Error types specific to this use case (if any)
```

Keep related code together. One file per major type is common but not required.
The goal is that someone looking at the directory listing can guess what each file contains.
