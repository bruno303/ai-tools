# RFC examples

These examples illustrate the workflow and scale, not domain-specific designs.

## Small feature: concise RFC

**Status:** Proposed

**Problem:** Users need a quick way to retry a failed, local operation.

**Goals:** Make retry behavior explicit and preserve the existing success
contract. **Non-goal:** redesign the operation or its storage.

**Evidence:** The issue's “Retry behavior” section states that retry is
user-visible (**source fact**, `retry-issue.md`, “Retry behavior”); nearby
commands already expose a bounded retry setting (**repository evidence**,
`cmd/sync.go`, `RunSync`). It is therefore a **technical inference** that the
feature should reuse the existing setting.

**Proposal:** Add the retry affordance at the existing command boundary, use
the established bounded policy, and report the final error unchanged. Verify
success, exhaustion, and a second invocation in the existing command tests.

**Trade-off:** Reusing the policy limits configurability but avoids a new
contract and keeps this small change predictable. No unresolved material
decisions remain.

## Larger feature: architectural decisions

**Status:** Proposed

**Summary:** Introduce a shared capability used by several independently
deployed components.

**Context and evidence:** The “Compatibility” section of the requirements
identifies the capability and its compatibility goal (**source facts**,
`capability-prd.md`, “Compatibility”). Repository guidance requires versioned
interfaces (**repository evidence**, `AGENTS.md`, “API conventions”). The need
for an adapter at each existing boundary is a **technical inference**.

**Design:** Define a versioned interface, keep component-specific adapters at
the integration boundaries, and make the shared service stateless. Describe
the request flow, timeout and retry behavior, error contract, ownership,
authentication, and telemetry. Compare a shared service with a library and a
central queue; choose the service because independent deployment is a goal
(**proposed decision**).

**Reliability and rollout:** Set an explicit timeout, bound retries, make
operations idempotent where retries can duplicate work, and use a compatibility
window with metrics before removing the old path. Include migration and
rollback triggers, security review, contract tests, and failure-mode analysis.

**Design risks:** A version mismatch could make adapters diverge from the
shared contract; mitigate with version negotiation and contract tests.

**Delivery risks:** Independently deployed components may not adopt the
compatibility window together; mitigate with staged rollout metrics and a
documented rollback trigger.

## Incomplete or conflicting sources: clarification and draft

**Status: DRAFT RFC — blocked on product decisions**

**Known:** The “Existing users” section of the PRD requires the behavior for
existing users (**source fact**, `behavior-prd.md`, “Existing users”). The issue
says the operation is asynchronous (**source fact**, `behavior-issue.md`,
“Completion”), but the supporting note says callers must receive the final
result immediately (**contradiction**, `caller-note.md`, “Response timing”).
Existing interfaces provide no precedent (**repository evidence**,
`internal/operations.go`, `OperationClient`).

**Safe inference:** Preserve the current authentication and error conventions
because the repository uses them consistently (**technical inference**, also
recorded as an **assumption** until confirmed).

**Batched questions:**

1. Should the public contract be asynchronous with a status resource, or
   synchronous with a bounded wait? This changes the interface and failure
   behavior.
2. If asynchronous, which source defines completion semantics and what is the
   retry/idempotency rule?

These independent, material questions are asked together. The draft still
records goals, constraints, candidate designs, affected interactions, and the
trade-offs so review can proceed without pretending that the contradiction is
resolved.
