# Agentic Coding Benchmarks

This directory contains a small, harness-agnostic benchmark runner for comparing models, harnesses, skills, and workflows on repeatable coding tasks.

The benchmark intentionally treats each agent setup as an executable command. It does not need to understand OpenCode, Codex, Claude Code, Superpowers, or any particular skill system.

## Goals

Measure whether extra workflow machinery actually improves outcomes enough to justify its cost.

Primary signals are deterministic:

- harness command completed successfully
- build/tests/lint or other scenario verification passed
- hidden benchmark tests passed
- wall-clock duration

Optional usage metadata can add token counts, model calls, or subagent calls when a harness can export them.

## Concepts

### Scenario

Defines **what must be solved**. A scenario owns:

- an isolated fixture repository/directory
- the task prompt
- post-run hidden-test injection
- deterministic verification commands
- timeout

### Variant

Defines **how the task is attempted**. A variant can represent any combination of:

- model
- harness
- skills/workflow
- setup commands
- environment variables
- execution command

### Result

Each execution writes an independent JSON result under `benchmarks/results/`. Repeated runs are kept separately so success rate and median cost can be compared instead of trusting one nondeterministic run.

## Quick start

Copy the example variant and adjust the harness/model command:

```bash
cp benchmarks/variants/opencode.example.json benchmarks/variants/local.json
```

Run the starter scenario:

```bash
python3 benchmarks/benchmark.py run \
  benchmarks/scenarios/normalize-username/scenario.json \
  benchmarks/variants/local.json
```

Run regular scenarios through the Make target; it intentionally excludes the
expensive Django fixture:

```bash
make benchmark-all
```

Do not use a broad `benchmarks/scenarios/*/scenario.json` glob: it can launch
the costly Django benchmark. To run selected scenarios directly, name them
explicitly (scenario arguments may also be directories):

```bash
python3 benchmarks/benchmark.py run \
  benchmarks/scenarios/normalize-username/scenario.json \
  benchmarks/scenarios/fix-invoice-total/scenario.json \
  benchmarks/variants/local.json
```

For the Django scenario, opt in with `make benchmark-large` or name it
explicitly in a direct runner command:

```bash
make benchmark-large VARIANT=benchmarks/variants/local.json
python3 benchmarks/benchmark.py run \
  benchmarks/scenarios/django-complex-change/scenario.json \
  benchmarks/variants/local.json
```

`SCENARIOS` overrides the regular set used by `benchmark-all`; it does not
change `benchmark-large`. Use `LARGE_SCENARIO` to change the single scenario
used by `benchmark-large`. `VARIANT`, `REPEAT`, `RESULTS_DIR`, and
`BENCHMARK_ARGS` are also overridable. `make benchmark` remains the
starter-scenario target.

Run it five times:

```bash
python3 benchmarks/benchmark.py run \
  benchmarks/scenarios/normalize-username/scenario.json \
  benchmarks/variants/local.json \
  --repeat 5
```

Compare saved executions:

```bash
python3 benchmarks/benchmark.py compare benchmarks/results/*.json
```

The comparison prints a Markdown table with scenario, variant, run count,
success rate, median wall-clock time, and median input tokens when available.
Use `--scenario NAME` and/or `--variant NAME` for exact-match filters. Use
`--since TIMESTAMP` to include only results whose `started_at` is at or after
an ISO-8601 timestamp (including its timezone):

```bash
python3 benchmarks/benchmark.py compare benchmarks/results/*.json \
  --since 2026-09-10T12:00:00Z
```

Each execution prints a header with its progress, scenario, variant, repeat
number, and timeout, followed by a PASS/FAIL summary and result path. While a
 command is running without `--verbose` or `--quiet`, the runner emits a
 heartbeat about every 15 seconds with elapsed time and timeout. Pass
 `--verbose` to stream captured stdout and stderr live with stream prefixes, or
 `--quiet` to suppress heartbeats and streaming while keeping the header and
final summary. Use `--repeat N` for repeated executions. Prefer `--repeat 3`
to `--repeat 5` for a practical estimate of nondeterministic performance; use
more only when the decision warrants the additional cost. Use
`--keep-workspace` to retain the temporary workspace,
and `--results-dir DIR` to write result JSON files somewhere other than the
default `benchmarks/results/` directory.

Result filenames include a UTC timestamp with microseconds and a per-process
counter, so fast repeats and batch runs remain separate.

Every setup, agent, and verification command runs in its own process group.
The fixture on disk is copied into a fresh temporary workspace (initialized as a
git repository) for each execution and is never modified. On timeout and after a
run, the runner terminates the whole process group, including leftover harness
child processes, before the next execution.

## Scenario format

```json
{
  "name": "scenario-name",
  "fixture": "fixture",
  "task": "task.md",
  "timeout_seconds": 600,
  "inject_after_run": [
    {
      "source": "hidden-tests/test_hidden.py",
      "destination": "test_hidden.py"
    }
  ],
  "verification": [
    {
      "name": "tests",
      "command": ["python3", "-m", "unittest", "discover", "-v"]
    }
  ]
}
```

`inject_after_run` happens only after the agent command exits. This keeps hidden evaluators outside the workspace while the model is solving the task.

The runner also accepts an external Git fixture. Its configuration must use a
URL and a full 40-character commit SHA; a tag, branch, or abbreviated SHA is
rejected. For example:

```json
{
  "name": "django-complex-change",
  "fixture": {
    "url": "https://github.com/django/django.git",
    "commit": "467aeeb569da17a7573e8dfc4932434c84e70642"
  },
  "task": "task.md",
  "timeout_seconds": 1800,
  "token_target": {"metric": "input_tokens", "minimum": 400000},
  "inject_after_run": [{"source": "hidden-tests/test_hidden.py", "destination": "test_hidden.py"}],
  "verification": [{"name": "hidden behavioral tests", "command": "python3 -m unittest test_hidden -v"}]
}
```

For a repository shipped with the scenario, use a relative fixture directory,
for example `"fixture": "fixture"`. External checkouts are cached under
`$BENCHMARK_FIXTURE_CACHE`, defaulting to `~/.cache/ai-tools-benchmark/`. The
cache key includes the URL and commit, and the runner verifies that both the
requested object and `HEAD` match the pinned commit and that the worktree is
clean before reuse. Cache publication uses an OS-level lock that is released
automatically if a process terminates. Remove an entry or the whole cache when
it should be refetched; the runner publishes repaired checkouts through a temporary
directory. External fixture cloning and checkout
failures are reported as `failure_reason: "fixture_setup_failed"` with
`fixture_error`. Do not run external fixtures without network access, and
review their provenance and license before use: a Git SHA makes the source
reproducible, not necessarily safe or licensed for every purpose.

Injection destinations are checked immediately before copying and must remain
inside the workspace without symlink traversal. A rejected or failed hidden-test
injection produces `failure_reason: "injection_failed"` and `injection_error`;
verification commands are not run after such a failure. The runner retains an
open workspace descriptor across the agent process and uses descriptor-relative,
atomic replacement for injected files, so workspace replacement and existing
hard links cannot redirect hidden-test writes.

Verification should test behavior rather than prescribe a specific implementation. Avoid assertions about exact file structure unless file placement is part of the requirement.

## Variant format

Prefer argument arrays. Commands are executed directly without a shell:

```json
{
  "name": "opencode-gpt56-baseline",
  "command": ["opencode2", "run", "--model", "openai/gpt-5.6", "{task_content}"],
  "setup": [],
  "env": {}
}
```

Simple command strings are also accepted and are parsed with `shlex.split`, but shell syntax such as pipes, redirects, `&&`, or command substitution is intentionally unsupported.

Available placeholders in `command` and `setup`:

- `{task_file}` - absolute path to the task Markdown file
- `{task_content}` - complete task Markdown content passed as one argument
- `{workspace}` - isolated fixture workspace

Commands execute with the workspace as their current directory. Each workspace
is initialized as its own fresh git repository (baseline commit of the fixture)
and `PWD` is set to it, so harness tooling roots itself inside the sandbox
instead of an enclosing repository. If your harness has a working-directory
flag, use it when necessary for that harness. The benchmark runner already
starts each command in the isolated workspace, and the OpenCode 2 variants
inherit that working directory directly.

### Optional usage metrics

A variant may set `usage_file` to a JSON file that its harness or wrapper creates inside the workspace:

```json
{
  "name": "instrumented-run",
  "command": ["./run-agent-and-export-usage.sh", "{task_file}"],
  "usage_file": ".benchmark-usage.json"
}
```

The runner stores the file contents under the result's `usage` field. `compare` understands `input_tokens` when provided. Other metrics remain available in the raw result for future analysis.

A useful usage payload is:

```json
{
  "input_tokens": 850000,
  "cached_input_tokens": 700000,
  "output_tokens": 12000,
  "model_calls": 14,
  "subagent_calls": 5
}
```

Usage collection is optional because different harnesses expose telemetry differently.

### Token targets and result semantics

`token_target` currently supports the `input_tokens` metric and a non-negative
`minimum`. The runner records the result as `token_qualification` (and the
backward-compatible `qualification`) with `metric`, `minimum`, `actual`, and
`met`. Missing usage, missing `input_tokens`, or a run below the minimum means
the run does not qualify; it is not a correctness failure. Correctness
`success` is independent: it is true when the command exits successfully and
all verification commands pass, regardless of whether a token target was met.
For the Django scenario, the 400,000-input-token target is a qualification
threshold, while its 1,800-second timeout describes the possible runtime and
why it is opt-in—not a promise that every run consumes exactly that many tokens
or lasts that long.

When a result is compared, the Markdown table reports runs, success rate,
median duration, median input tokens (or `n/a` when unavailable), and
qualifying runs. Raw results preserve usage fields such as
`cached_input_tokens`, `output_tokens`, `model_calls`, and `subagent_calls`.
For an external fixture, `fixture_provenance` records its `url` and normalized
full `commit` SHA on successful setup (and during configuration validation).
Configuration failures use `scenario_configuration_failed` with
`scenario_error`; fixture I/O failures use `fixture_setup_failed` with
`fixture_error`.

Treat usage metrics as cost signals alongside success rate and duration. The
runner reports median `input_tokens` in `compare`; raw result JSON also
preserves `cached_input_tokens`, `output_tokens`, `model_calls`,
`subagent_calls`, and other exported fields when present.

### OpenCode security

The example OpenCode variants pass `--auto`, which approves tool actions
automatically. Run them only in the benchmark's disposable isolated
workspace, and review the command, model, setup, and environment before using
a local variant. Do not use `--auto` with untrusted tasks or a workspace
containing secrets.

The OpenCode benchmark variants copy `opencode-noninteractive.jsonc` into each
temporary workspace and verify it with `opencode2 debug config` before running.
That config only allows `external_directory` and `read` access to
`$HOME/.agents/skills/*`; it does not deny the question permission. Prompts
also instruct agents to work unattended: they must not ask questions, invoke
the question tool, or wait for user input, and should resolve ambiguity from
the task, repository conventions, and reasonable assumptions.

### Result hygiene

Result files are local artifacts. If a result JSON is invalid or incomplete,
remove it from the glob or move it to a quarantine directory before running
`compare`; do not treat it as benchmark data. Invalid result JSONs are ignored
local artifacts and are not currently tracked in this repository.

## Designing scenarios

Build a balanced suite rather than scenarios optimized for a particular workflow:

- small mechanical change
- localized bug
- small feature following an obvious existing pattern
- API/domain/test change
- ambiguous bug requiring repository investigation
- multi-component feature
- refactor or architectural change
- feature with important failure/edge-case behavior

Include tasks where extra skills should provide little value. Otherwise the benchmark will be biased toward proving that more orchestration is better.

Prefer hidden deterministic tests as the primary correctness signal. A separate LLM/code-review verdict can be recorded later as a secondary qualitative metric, but should not replace executable evidence.

The current suite includes:

- `normalize-username` - a small mechanical input-normalization change for trimming, lowercasing, and rejecting empty usernames.
- `deactivate-user` - a service/API domain change covering user persistence, idempotent deactivation, and unknown-user errors.
- `fix-invoice-total` - a localized billing bug requiring integer-cent arithmetic and half-up discount rounding.
- `session-expiry` - an investigation of deterministic idle-session expiry across datetime inputs.
- `implement-sliding-window` - a rate-limiter feature following the existing fixed-window implementation while enforcing a rolling request limit.
- `split-datetime-helpers` - a structural refactor splitting parsing and formatting helpers while preserving compatibility imports and behavior.

## Fair comparisons

For meaningful comparisons:

1. Start every variant from the same scenario fixture.
2. Keep task wording identical.
3. Use the same verification and hidden tests.
4. Run each variant multiple times.
5. Compare success rate together with time/tokens, not quality in isolation.
6. Do not expose hidden tests to the agent during execution.

A workflow that raises success from 60% to 95% may justify higher token use. A workflow that keeps success at 100% while multiplying runtime and tokens probably does not.
