# Interface Design

Interfaces in Go are the primary tool for decoupling and testability. But they're also
the most common source of over-engineering. This guide helps you use them well.

## The Core Rule: Accept Interfaces, Return Structs

This principle drives most good Go API design:

```go
// Constructor returns a concrete type
func NewOrderService(repo OrderRepository, notifier Notifier) *OrderService {
    return &OrderService{repo: repo, notifier: notifier}
}

// Methods accept interfaces for flexibility
func ProcessPayment(ctx context.Context, processor PaymentProcessor, amount Money) error {
    return processor.Charge(ctx, amount)
}
```

Why:
- Returning structs gives callers access to the full API, including methods added later
- Accepting interfaces lets callers pass any implementation (real, mock, stub)
- It avoids the "interface upgrade" problem where adding a method breaks all implementors

## Keep Interfaces Small

The best Go interfaces have 1-3 methods. If your interface has more than 5, you likely
have a design issue — you're defining a role, not a capability.

```go
// Good — focused capabilities
type Reader interface {
    Read(ctx context.Context, id string) (*Entity, error)
}

type Writer interface {
    Save(ctx context.Context, entity *Entity) error
}

// Compose when needed
type ReadWriter interface {
    Reader
    Writer
}
```

```go
// Questionable — this is a class, not an interface
type Repository interface {
    Create(ctx context.Context, e *Entity) error
    GetByID(ctx context.Context, id string) (*Entity, error)
    Update(ctx context.Context, e *Entity) error
    Delete(ctx context.Context, id string) error
    List(ctx context.Context, filter Filter) ([]*Entity, error)
    Count(ctx context.Context, filter Filter) (int, error)
    Search(ctx context.Context, query string) ([]*Entity, error)
    BatchCreate(ctx context.Context, entities []*Entity) error
}
// Ask: does any consumer actually use ALL of these methods?
// Usually not — split by what each consumer needs.
```

## When to Create an Interface

**Do create an interface when:**
- You need to mock a dependency in tests
- Multiple implementations exist (or will exist)
- You're defining a boundary between packages

**Don't create an interface when:**
- There's only one implementation and no tests need mocking
- You're wrapping a struct "just in case"
- The interface would have the same methods as the only struct that implements it

Wait until you have a concrete need. Go's implicit interface satisfaction means you can
add an interface later without changing the implementation.

## Compile-Time Verification

Catch missing method implementations at compile time, not runtime:

```go
var _ OrderRepository = (*PostgresOrderRepo)(nil)
var _ PaymentProcessor = (*StripeProcessor)(nil)
```

Place these at the top of the implementation file. The compiler will error if the struct
doesn't satisfy the interface.

## Functional Options

For constructors with many optional parameters, use functional options:

```go
type Option func(*Client)

func WithTimeout(d time.Duration) Option {
    return func(c *Client) { c.timeout = d }
}

func WithRetries(n int) Option {
    return func(c *Client) { c.maxRetries = n }
}

func WithLogger(l *slog.Logger) Option {
    return func(c *Client) { c.logger = l }
}

func NewClient(baseURL string, opts ...Option) *Client {
    c := &Client{
        baseURL:    baseURL,
        timeout:    30 * time.Second,  // sensible defaults
        maxRetries: 3,
        logger:     slog.Default(),
    }
    for _, opt := range opts {
        opt(c)
    }
    return c
}
```

When to use functional options vs a config struct:
- **Functional options**: public API, many optional settings, need defaults
- **Config struct**: internal code, all fields usually set, simpler to read

## Common Standard Library Interfaces

Know these — they're the lingua franca of Go:

| Interface | Package | Use |
|-----------|---------|-----|
| `io.Reader` | `io` | Anything that produces bytes |
| `io.Writer` | `io` | Anything that consumes bytes |
| `io.Closer` | `io` | Anything with cleanup |
| `fmt.Stringer` | `fmt` | Custom string representation |
| `error` | builtin | Error values |
| `sort.Interface` | `sort` | Custom sorting |
| `http.Handler` | `net/http` | HTTP request handling |
| `encoding.TextMarshaler` | `encoding` | Custom text serialization |
| `json.Marshaler` | `encoding/json` | Custom JSON serialization |

When your type naturally fits one of these, implement it — the entire ecosystem benefits.
