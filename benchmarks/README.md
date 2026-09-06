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

The comparison prints a Markdown table with run count, success rate, median wall-clock time, and median input tokens when available.

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
      "command": "python3 -m unittest discover -v"
    }
  ]
}
```

`inject_after_run` happens only after the agent command exits. This keeps hidden evaluators outside the workspace while the model is solving the task.

Verification should test behavior rather than prescribe a specific implementation. Avoid assertions about exact file structure unless file placement is part of the requirement.

## Variant format

```json
{
  "name": "opencode-gpt56-baseline",
  "command": "opencode run --model openai/gpt-5.6 \"$(cat '{task_file}')\"",
  "setup": [],
  "env": {}
}
```

Available placeholders in `command` and `setup`:

- `{task_file}` - absolute path to the task Markdown file
- `{workspace}` - isolated fixture workspace

Commands execute with the workspace as their current directory.

### Optional usage metrics

A variant may set `usage_file` to a JSON file that its harness or wrapper creates inside the workspace:

```json
{
  "name": "instrumented-run",
  "command": "./run-agent-and-export-usage.sh '{task_file}'",
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

## Fair comparisons

For meaningful comparisons:

1. Start every variant from the same scenario fixture.
2. Keep task wording identical.
3. Use the same verification and hidden tests.
4. Run each variant multiple times.
5. Compare success rate together with time/tokens, not quality in isolation.
6. Do not expose hidden tests to the agent during execution.

A workflow that raises success from 60% to 95% may justify higher token use. A workflow that keeps success at 100% while multiplying runtime and tokens probably does not.
