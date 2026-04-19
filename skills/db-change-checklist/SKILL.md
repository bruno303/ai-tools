---
name: db-change-checklist
description: Use when changing schemas, queries, indexes, persistence rules, or migrations so database risks are identified before rollout.
---

# When to use
Use for:
- schema changes
- new migrations
- query behavior changes
- index changes
- backfills and data corrections

Do not use for:
- pure API changes with no persistence impact
- superficial code cleanup around repositories without behavior change

# Goal
Make database changes safe, compatible, and observable.

# Checklist
Confirm when relevant:
- schema or data migration required
- backward compatibility window
- locking or long-running migration risk
- index and query performance impact
- backfill strategy and batching
- rollback or safe forward-fix path
- transaction boundaries
- data correctness validation after rollout
- operational observability and alerts

# Rules
- Prefer expand-and-contract patterns for risky changes.
- Call out destructive or blocking operations explicitly.
- Distinguish schema change, data migration, and application change responsibilities.

# Output
Provide:
- change type and affected tables or queries
- migration and rollout risks
- compatibility considerations
- validation and rollback notes
