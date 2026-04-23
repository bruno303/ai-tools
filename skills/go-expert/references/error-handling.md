# Error Handling Strategy

Go errors are values. This means you design your error strategy the same way you design
your data model — intentionally, based on what callers need.

## The Three Error Strategies

### 1. Sentinel Errors — for well-known, expected conditions

Use when: the caller needs to check for a specific, named condition.

```go
package order

import "errors"

var (
    ErrNotFound     = errors.New("order not found")
    ErrAlreadyPaid  = errors.New("order already paid")
    ErrInvalidState = errors.New("invalid order state transition")
)
```

Callers check with `errors.Is`:
```go
if errors.Is(err, order.ErrNotFound) {
    // handle missing order
}
```

When NOT to use: if the caller also needs structured data about the error (use a custom type instead).

### 2. Custom Error Types — for errors that carry data

Use when: the caller needs to inspect error details, not just identity.

```go
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed on %s: %s", e.Field, e.Message)
}

// Multiple validation failures
type ValidationErrors []ValidationError

func (e ValidationErrors) Error() string {
    msgs := make([]string, len(e))
    for i, v := range e {
        msgs[i] = v.Error()
    }
    return strings.Join(msgs, "; ")
}
```

Callers inspect with `errors.As`:
```go
var valErr *ValidationError
if errors.As(err, &valErr) {
    log.Printf("field %s: %s", valErr.Field, valErr.Message)
}
```

### 3. Wrapped Errors — for adding context without changing identity

Use when: the caller doesn't need to distinguish this specific failure, but debugging needs context.

```go
func (s *Service) GetOrder(ctx context.Context, id string) (*Order, error) {
    o, err := s.repo.FindByID(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("get order %s: %w", id, err)
    }
    return o, nil
}
```

The `%w` verb preserves the error chain — callers can still use `errors.Is` and `errors.As`
on the original error.

## Decision Flowchart

```
Is this a well-known condition the caller must handle?
├── Yes → Does the caller need data beyond identity?
│         ├── Yes → Custom error type
│         └── No  → Sentinel error
└── No  → Wrap with context: fmt.Errorf("doing X: %w", err)
```

## Error Wrapping Guidelines

**Add context that helps debugging:**
```go
// Good — tells you what operation failed and with what input
return fmt.Errorf("fetch user %s from cache: %w", userID, err)

// Bad — adds nothing useful
return fmt.Errorf("error: %w", err)

// Bad — loses the error chain (no %w)
return fmt.Errorf("fetch user failed: %v", err)
```

**Don't wrap at every layer.** If three layers all wrap the same error, you get:
`"handle request: process order: save to database: connection refused"`.
That's actually fine for debugging — but each layer should add *new* information.
If a layer has nothing to add, just return the error as-is.

## Boundary Error Mapping

Map errors to transport codes at the handler layer, not inside business logic.

```go
func (h *Handler) GetOrder(w http.ResponseWriter, r *http.Request) {
    order, err := h.service.GetOrder(r.Context(), orderID)
    if err != nil {
        switch {
        case errors.Is(err, order.ErrNotFound):
            http.Error(w, "order not found", http.StatusNotFound)
        case errors.As(err, new(*ValidationError)):
            http.Error(w, err.Error(), http.StatusBadRequest)
        default:
            // Log the full error for debugging, return generic message to client
            slog.ErrorContext(r.Context(), "unexpected error", "error", err)
            http.Error(w, "internal error", http.StatusInternalServerError)
        }
        return
    }
    // write success response
}
```

The business logic layer should never import `net/http` or know about status codes.

## Error Handling Anti-Patterns

**Don't use panic for control flow.** Panic is for truly unrecoverable situations
(programmer bugs, impossible states). If it can happen in production, it needs an error return.

**Don't log and return.** Pick one. If you log an error and also return it, the caller
will likely log it again, and you get duplicate noise.

```go
// Bad
func doThing() error {
    if err := step(); err != nil {
        log.Printf("step failed: %v", err)  // logged here
        return err                            // ...and again by caller
    }
    return nil
}

// Good — return with context, let the handler log
func doThing() error {
    if err := step(); err != nil {
        return fmt.Errorf("step in doThing: %w", err)
    }
    return nil
}
```

**Don't ignore errors with `_` without a comment explaining why.**
```go
// Bad
_ = file.Close()

// Acceptable — documented reason
_ = file.Close() // best-effort cleanup; write already succeeded
```
