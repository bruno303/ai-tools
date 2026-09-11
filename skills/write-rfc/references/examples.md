# RFC examples

These examples illustrate the workflow and scale, not domain-specific designs.

## Small feature: concise RFC

**Status:** Proposed

**Problem:** Users need a quick way to retry a failed, local operation.

**Goals:** Make retry behavior explicit and preserve the existing success
contract. **Non-goal:** redesign the operation or its storage.

**Evidence:** The issue's “Retry behavior” section states that retry is
user-visible (`retry-issue.md`, “Retry behavior”). Nearby commands already
expose a bounded retry setting (`cmd/sync.go`, `RunSync`), so reusing that
policy is consistent with the current repository.

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
identifies the capability and its compatibility goal
(`capability-prd.md`, “Compatibility”). Repository guidance requires versioned
interfaces (`AGENTS.md`, “API conventions”). Based on those constraints, the
proposal uses an adapter at each existing boundary.

**Design:** Define a versioned interface, keep component-specific adapters at
the integration boundaries, and make the shared service stateless. Describe
the request flow, timeout and retry behavior, error contract, ownership,
authentication, and telemetry. Compare a shared service with a library and a
central queue; choose the service because independent deployment is a goal.

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
existing users (`behavior-prd.md`, “Existing users”). The issue says the
operation is asynchronous (`behavior-issue.md`, “Completion”), while the
supporting note says callers must receive the final result immediately
(`caller-note.md`, “Response timing”). Existing interfaces provide no precedent
(`internal/operations.go`, `OperationClient`).

**Contradiction:** The asynchronous completion requirement and immediate final
response requirement cannot both define the public contract.

**Assumption:** Preserve the current authentication and error conventions
because the repository uses them consistently. This assumption does not resolve
the response-timing contradiction.

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
