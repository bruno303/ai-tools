# Observability Patterns

## Core Rules

- Prefer structured logs (key/value) over free-form strings.
- Use `context.Context` in all request-scoped logging and tracing paths.
- Include correlation identifiers (`trace_id`, `span_id`, `request_id`, `user_id` when allowed).
- Log at boundaries (incoming request, outgoing dependency call, background job start/end).
- Avoid logging secrets, tokens, passwords, full PII, or large payload dumps.
- Emit actionable logs: state what failed, where, and why.

## Logging Levels and Intent

- `DEBUG`: diagnostic details for local/dev troubleshooting.
- `INFO`: key lifecycle events and normal business milestones.
- `WARN`: recoverable anomalies, retries, partial degradation.
- `ERROR`: failed operation requiring handling or user impact.

Use level conventions consistently across services so alerts and dashboards remain reliable.

## Structured Logging With `log/slog` (Go 1.21+)

```go
package logging

import (
    "context"
    "log/slog"
    "os"
)

func NewLogger(service, env, version string) *slog.Logger {
    handler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level: slog.LevelInfo,
    })
    return slog.New(handler).With(
        slog.String("service", service),
        slog.String("env", env),
        slog.String("version", version),
    )
}

func LogOrderCreated(ctx context.Context, logger *slog.Logger, orderID, userID string, amount int64) {
    logger.InfoContext(ctx, "order created",
        slog.String("order_id", orderID),
        slog.String("user_id", userID),
        slog.Int64("amount_cents", amount),
    )
}
```

## Attach Trace Context to Logs

If OpenTelemetry tracing is enabled, enrich logs with trace and span IDs so operators can pivot from logs to traces quickly.

```go
package logging

import (
    "context"
    "log/slog"

    "go.opentelemetry.io/otel/trace"
)

func WithTraceFields(ctx context.Context, logger *slog.Logger) *slog.Logger {
    spanCtx := trace.SpanFromContext(ctx).SpanContext()
    if !spanCtx.IsValid() {
        return logger
    }
    return logger.With(
        slog.String("trace_id", spanCtx.TraceID().String()),
        slog.String("span_id", spanCtx.SpanID().String()),
    )
}
```

## Middleware Pattern (HTTP)

```go
func LoggingMiddleware(base *slog.Logger, next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()

        reqID := r.Header.Get("X-Request-ID")
        logger := base.With(
            slog.String("request_id", reqID),
            slog.String("method", r.Method),
            slog.String("path", r.URL.Path),
        )
        logger = WithTraceFields(r.Context(), logger)

        logger.InfoContext(r.Context(), "request started")
        next.ServeHTTP(w, r)
        logger.InfoContext(r.Context(), "request completed",
            slog.Int64("duration_ms", time.Since(start).Milliseconds()),
        )
    })
}
```

## Error Logging Pattern

```go
func handlePayment(ctx context.Context, logger *slog.Logger, id string) error {
    if err := charge(ctx, id); err != nil {
        // Log once at the boundary where the error becomes actionable.
        logger.ErrorContext(ctx, "charge failed",
            slog.String("payment_id", id),
            slog.String("error", err.Error()),
        )
        return fmt.Errorf("charge payment %s: %w", id, err)
    }
    return nil
}
```

Guidance:
- Avoid duplicate logs for the same error across every stack layer.
- Add domain identifiers (`payment_id`, `tenant_id`, `job_id`) to speed triage.
- Return wrapped errors (`%w`) so callers can classify failures.

## Tracing Pattern (OpenTelemetry)

```go
var tracer = otel.Tracer("orders-service")

func (s *Service) CreateOrder(ctx context.Context, in CreateOrderInput) error {
    ctx, span := tracer.Start(ctx, "Service.CreateOrder",
        trace.WithAttributes(
            attribute.String("order.customer_id", in.CustomerID),
            attribute.Int("order.items", len(in.Items)),
        ),
    )
    defer span.End()

    if err := s.repo.Save(ctx, in); err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, "save order failed")
        return fmt.Errorf("save order: %w", err)
    }

    span.SetStatus(codes.Ok, "ok")
    return nil
}
```

Tracing rules:
- Start spans at service boundaries and dependency calls.
- Record errors on spans (`RecordError`) and set explicit status.
- Keep span names stable (`Package.Func` or operation style) for reliable dashboards.
- Add low-cardinality attributes; avoid unbounded values.

## Metrics and Logging Together

- Emit metrics for rates/latency/errors; use logs for rich incident context.
- Prefer counters/histograms over high-cardinality label explosions.
- Correlate telemetry dimensions across logs, metrics, and traces (`service`, `route`, `tenant` when safe).

## Production Checklist

- Ensure JSON logs in production and human-readable logs in local dev if preferred.
- Define a redaction policy for sensitive fields.
- Verify log volume and sampling strategy for noisy paths.
- Confirm trace propagation across HTTP/gRPC clients and handlers.
- Ensure alerting is driven by metrics/SLOs, not raw log volume alone.
