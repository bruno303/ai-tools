# RFC planning examples

These compact examples show proportional decomposition and RFC traceability.

## Small RFC: one task

RFC §2 selects a nullable `timezone` on the profile record; §4 requires old
clients to continue working; §6 accepts read/write coverage. Keep it together:

```markdown
### Task 1: Add profile timezone support
- **Objective:** Persist and expose optional `timezone` without breaking old clients.
- **Repository area:** profile persistence, API serialization, migration, and focused tests.
- **Expected changes/scope:** Add the nullable field, compatible serialization, migration, and focused tests.
- **Expected writable outputs:**
  - `profiles/model.py` (modified)
  - `profiles/serializers.py` (modified)
  - `profiles/migrations/0004_add_timezone.py` (created)
  - `profiles/tests/test_timezone.py` (created)
- **Dependencies:** none
- **Validation:** profile unit/API tests; migration applies and old payloads remain valid.
```

## Medium RFC: dependent tasks

RFC §3 chooses a token issuer; §5 requires existing tokens to remain valid;
§7 requires metrics. Separate the shared foundation from its consumer:

```markdown
### Task 1: Add issuer and verification contract
- **Objective:** Implement the RFC §3 issuer abstraction and compatibility rules from §5.
- **Repository area:** issuer implementation, token configuration, and auth unit tests.
- **Expected changes/scope:** Add implementation, configuration, and contract tests.
- **Expected writable outputs:**
  - `auth/issuer.py` (created)
  - `auth/config.py` (modified)
  - `auth/tests/test_issuer.py` (created)
- **Dependencies:** none
- **Validation:** issuer and backward-compatibility tests.

### Task 2: Wire login and metrics
- **Objective:** Use the issuer at login and emit the §7 success/failure metrics.
- **Repository area:** login endpoint, authentication integration tests, and metrics module.
- **Expected changes/scope:** Connect Task 1, preserve response contract, and test instrumentation.
- **Expected writable outputs:**
  - `auth/login.py` (modified)
  - `auth/metrics.py` (modified)
  - `auth/tests/test_login_integration.py` (modified)
- **Dependencies:** Task 1
- **Validation:** login integration tests and metric assertion.
```

## Large RFC: genuinely parallel work

RFC §4 selects one event schema and §8 requires both a dashboard and a client
adapter. After the schema contract is settled, these scopes do not overlap:

```markdown
### Task 1: Define event schema
- **Objective:** Publish the RFC §4 event contract and fixtures.
- **Repository area:** event schema package and schema contract tests.
- **Expected changes/scope:** Schema, version fixture, and compatibility validation.
- **Expected writable outputs:**
  - `events/schema.py` (created)
  - `events/fixtures/v2.json` (created)
  - `events/tests/test_schema_contract.py` (created)
- **Dependencies:** none
- **Validation:** schema/fixture contract tests.

### Task 2: Build dashboard integration
- **Objective:** Implement the §8 operational dashboard from the event stream.
- **Repository area:** dashboard configuration and dashboard validation tests.
- **Expected changes/scope:** Queries, panels, alerts, and dashboard validation.
- **Expected writable outputs:**
  - `ops/dashboard/events.json` (created)
  - `ops/dashboard/tests/test_events_dashboard.py` (created)
- **Dependencies:** Task 1
- **Validation:** dashboard/config validation and alert query tests.

### Task 3: Build client adapter
- **Objective:** Implement the §8 consumer adapter using the Task 1 schema.
- **Repository area:** client adapter package and adapter tests.
- **Expected changes/scope:** Mapping, retries required by RFC §6, and contract tests.
- **Expected writable outputs:**
  - `clients/adapter/client.py` (created)
  - `clients/adapter/tests/test_client.py` (created)
- **Dependencies:** Task 1
- **Validation:** adapter integration and retry tests.
```

Tasks 2 and 3 may run in isolated worktrees in parallel: neither depends on
the other and their repository scopes do not conflict. The execution workflow
owns that dispatch decision.

## Material unresolved detail: concise clarification

RFC §5 requires “safe rollout” but does not say whether writes are dual-read,
dual-written, or backfilled. Repository inspection found both patterns and no
precedent for this data. Ask one bounded question before planning:

> For the §5 rollout, should deployment use (A) a backward-compatible
> backfill, (B) dual-write/read with a later cutover, or (C) a coordinated
> breaking migration? This determines migration code, deploy ordering, and
> rollback validation.

Do not ask about naming or test framework when repository conventions already
settle those details.
