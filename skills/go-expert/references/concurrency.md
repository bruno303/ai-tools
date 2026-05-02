# Concurrency Patterns

Go's concurrency model is powerful but unforgiving. A goroutine leak is a memory leak.
A missing `select` on `ctx.Done()` is a hung process. This guide helps you pick the
right tool and use it safely.

## Choosing the Right Tool

### errgroup — your default for parallel work

When you have N independent tasks that should run concurrently and you want to stop on
the first error, `errgroup` is almost always the right choice.

```go
import "golang.org/x/sync/errgroup"

func fetchAll(ctx context.Context, urls []string) ([]Response, error) {
    g, ctx := errgroup.WithContext(ctx)
    results := make([]Response, len(urls))

    for i, url := range urls {
        g.Go(func() error {
            resp, err := fetch(ctx, url)
            if err != nil {
                return fmt.Errorf("fetch %s: %w", url, err)
            }
            results[i] = resp // safe: each goroutine writes to its own index
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return nil, err
    }
    return results, nil
}
```

Why errgroup over raw goroutines:
- Automatic `context` cancellation on first error
- Built-in `WaitGroup` semantics — no forgotten `wg.Done()`
- Optional concurrency limit with `g.SetLimit(n)`
- Clean error propagation

### Worker Pool — for bounded, long-lived concurrency

Use when you have a continuous stream of work and need to control resource usage.

```go
func processStream(ctx context.Context, jobs <-chan Job, workers int) error {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(workers)

    for job := range jobs {
        g.Go(func() error {
            return process(ctx, job)
        })
    }

    return g.Wait()
}
```

For more control (graceful drain, dynamic sizing), build a dedicated pool:

```go
type Pool struct {
    work chan func()
    done chan struct{}
}

func NewPool(size int) *Pool {
    p := &Pool{
        work: make(chan func(), size*2),
        done: make(chan struct{}),
    }
    var wg sync.WaitGroup
    wg.Add(size)
    for range size {
        go func() {
            defer wg.Done()
            for fn := range p.work {
                fn()
            }
        }()
    }
    go func() {
        wg.Wait()
        close(p.done)
    }()
    return p
}

func (p *Pool) Submit(fn func()) { p.work <- fn }
func (p *Pool) Shutdown()        { close(p.work); <-p.done }
```

### Channel Pipeline — for streaming transformations

Use when data flows through stages, each transforming or filtering.

```go
func pipeline(ctx context.Context, in <-chan RawEvent) <-chan ProcessedEvent {
    validated := stage(ctx, in, validate)
    enriched := stage(ctx, validated, enrich)
    return enriched
}

func stage[In, Out any](ctx context.Context, in <-chan In, fn func(context.Context, In) (Out, error)) <-chan Out {
    out := make(chan Out)
    go func() {
        defer close(out)
        for item := range in {
            result, err := fn(ctx, item)
            if err != nil {
                continue // or send to error channel
            }
            select {
            case out <- result:
            case <-ctx.Done():
                return
            }
        }
    }()
    return out
}
```

### sync.Mutex — for protecting shared state

```go
type SafeMap[K comparable, V any] struct {
    mu sync.RWMutex
    m  map[K]V
}

func (s *SafeMap[K, V]) Get(key K) (V, bool) {
    s.mu.RLock()
    defer s.mu.RUnlock()
    v, ok := s.m[key]
    return v, ok
}

func (s *SafeMap[K, V]) Set(key K, val V) {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.m[key] = val
}
```

Use `RWMutex` when reads vastly outnumber writes. But don't assume — benchmark first.
For simple cases, a regular `Mutex` has less overhead and fewer footguns.

## The Goroutine Lifecycle Rule

Every goroutine you launch must have a clear answer to: "What makes it stop?"

```go
// Good — goroutine stops when ctx is cancelled or channel closes
go func() {
    for {
        select {
        case item, ok := <-work:
            if !ok {
                return
            }
            process(item)
        case <-ctx.Done():
            return
        }
    }
}()

// Bad — goroutine runs forever if nobody closes `work`
go func() {
    for item := range work {
        process(item)
    }
}()
// Only acceptable if you can guarantee `work` will be closed.
```

## Graceful Shutdown

Every production service needs clean shutdown. Here's the pattern:

```go
func main() {
    ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
    defer stop()

    srv := &http.Server{Addr: ":8080", Handler: router}

    // Start server in background
    go func() {
        if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
            slog.Error("server error", "error", err)
        }
    }()

    slog.Info("server started", "addr", ":8080")

    // Block until signal
    <-ctx.Done()
    slog.Info("shutting down")

    // Give in-flight requests time to finish
    shutdownCtx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
    defer cancel()

    if err := srv.Shutdown(shutdownCtx); err != nil {
        slog.Error("shutdown error", "error", err)
    }
}
```

## Common Mistakes

**Goroutine leak from forgotten context check:**
```go
// Leaks if ctx is cancelled while channel is full
go func() {
    ch <- result // blocks forever if nobody reads
}()

// Fixed
go func() {
    select {
    case ch <- result:
    case <-ctx.Done():
    }
}()
```

**Race on loop variable (Go < 1.22):**
```go
// Bug in Go < 1.22: all goroutines see the last value of i
for i := range items {
    go func() { process(items[i]) }()
}

// Fix (unnecessary in Go 1.22+ but still clear)
for i := range items {
    go func() { process(items[i]) }()
}
// In Go 1.22+ the loop variable is per-iteration, so this is safe.
// In older Go, capture: i := i
```

**Using time.After in a loop (leaks timers):**
```go
// Bad — creates a new timer every iteration, old ones leak until they fire
for {
    select {
    case <-ch:
    case <-time.After(5 * time.Second): // leaked timer!
    }
}

// Good — reuse the timer
timer := time.NewTimer(5 * time.Second)
defer timer.Stop()
for {
    timer.Reset(5 * time.Second)
    select {
    case <-ch:
    case <-timer.C:
    }
}
```
