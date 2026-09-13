.DEFAULT_GOAL := help

PYTHON ?= python3
SCENARIO ?= benchmarks/scenarios/normalize-username/scenario.json
SCENARIOS ?= benchmarks/scenarios/*/scenario.json
VARIANT ?= benchmarks/variants/opencode.example.json
REPEAT ?= 1
RESULTS_DIR ?= benchmarks/results
BENCHMARK_ARGS ?=
COMPARE_ARGS ?=

.PHONY: help test validate-agents check benchmark benchmark-all variants compare

help: ## Show available commands and common variable overrides.
	@printf '%s\n' \
		'Available commands:' \
		'  make test            Run the Python unit tests.' \
		'  make validate-agents Validate active agent definitions.' \
		'  make check           Run tests and agent validation.' \
		'  make benchmark       Run the starter scenario.' \
		'  make benchmark-all   Run every benchmark scenario.' \
		'  make variants        List benchmark variant JSON files.' \
		'  make compare        Compare saved benchmark results.' \
		'' \
		'Variable overrides:' \
		'  PYTHON=python3 SCENARIO=... VARIANT=... REPEAT=... RESULTS_DIR=...' \
		'  BENCHMARK_ARGS=... COMPARE_ARGS=...'

test: ## Run the Python unit tests.
	$(PYTHON) -m unittest discover -s tests -v

validate-agents: ## Validate active agent definitions.
	$(PYTHON) scripts/validate-agent-definitions.py

check: test validate-agents ## Run all repository checks.

benchmark: ## Run the starter benchmark scenario.
	$(PYTHON) benchmarks/benchmark.py run $(SCENARIO) $(VARIANT) --repeat $(REPEAT) --results-dir $(RESULTS_DIR) $(BENCHMARK_ARGS)

benchmark-all: VARIANT := benchmarks/variants/gpt56-luna-subagent.json
benchmark-all: ## Run all benchmark scenarios.
	$(PYTHON) benchmarks/benchmark.py run $(SCENARIOS) $(VARIANT) --repeat $(REPEAT) --results-dir $(RESULTS_DIR) $(BENCHMARK_ARGS)

variants: ## List available benchmark variant JSON files.
	@find benchmarks/variants -maxdepth 1 -type f -name '*.json' -print | sort

compare: ## Compare JSON results in the results directory.
	@if test -z "$(strip $(wildcard $(RESULTS_DIR)/*.json))"; then \
		echo "No benchmark result JSON files found in $(RESULTS_DIR)." >&2; \
		exit 1; \
	fi
	$(PYTHON) benchmarks/benchmark.py compare $(wildcard $(RESULTS_DIR)/*.json) $(COMPARE_ARGS)
