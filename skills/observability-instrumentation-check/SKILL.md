---
name: observability-instrumentation-check
description: Use when adding or reviewing logs, metrics, traces, alerts, or instrumentation so operational visibility is sufficient and low-noise.
---

# When to use
Use for:
- new features needing monitoring
- bug fixes where visibility was missing
- changes to background jobs, integrations, retries, or failure handling
- review of existing instrumentation quality

Do not use for:
- purely cosmetic logging changes
- tasks with no operational behavior impact

# Goal
Ensure the change is observable in production with actionable, low-noise signals.

# Checklist
Confirm when relevant:
- important success and failure paths are visible
- logs include enough context without leaking sensitive data
- metrics cover throughput, latency, failures, and saturation where applicable
- traces include critical spans and useful attributes
- retries, timeouts, and downstream failures are visible
- alerts are tied to user or system impact, not just raw noise
- dashboards or queries can validate rollout behavior
- correlation identifiers or request identifiers are preserved across boundaries

# Rules
- Prefer structured logs.
- Avoid high-cardinality labels unless clearly justified.
- Do not log secrets, tokens, or sensitive payloads.
- Instrument business-critical boundaries and failure paths first.
- Favor signals that help diagnosis, not just signal volume.

# Output
Provide:
- instrumentation already present
- important gaps
- recommended logs, metrics, traces, or alerts
- privacy or cardinality concerns
