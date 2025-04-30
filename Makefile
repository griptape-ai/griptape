.PHONY: install
install: ## Install all dependencies.
	@make install/all

.PHONY: install/core
install/core: ## Install core dependencies.
	@uv sync

.PHONY: install/all
install/all: ## Install all dependencies.
	@uv sync --all-groups --all-extras

.PHONY: install/dev
install/dev: ## Install dev dependencies.
	@uv sync --group dev

.PHONY: install/test
install/test: ## Install test dependencies.
	@uv sync --group test

.PHONY: test  ## Run all tests.
test: test/unit test/integration

.PHONY: test/unit
test/unit: ## Run unit tests.
	@uv run pytest -n auto tests/unit

.PHONY: test/unit/%
test/unit/%: ## Run specific unit tests.
	@uv run pytest -n auto tests/unit -k $*

.PHONY: test/unit/coverage
test/unit/coverage:
	@uv run pytest -n auto --cov=griptape tests/unit
	@uv run coverage xml -i 

.PHONY: test/integration
test/integration:
	@uv run pytest -n auto tests/integration/test_code_blocks.py

.PHONY: lint
lint: ## Lint project.
	@uv run ruff check --fix

.PHONY: lint/fix
lint/fix: ## Lint project with unsafe fixes.
	@uv run ruff check --fix --unsafe-fixes

.PHONY: format
format: ## Format project.
	@uv run ruff format
	@uv run mdformat .github/ docs/

.PHONY: check
check: check/format check/lint check/types check/spell ## Run all checks.

.PHONY: check/format
check/format:
	@uv run ruff format --check
	@uv run mdformat --check .github/ docs/

.PHONY: check/lint
check/lint:
	@uv run ruff check

.PHONY: check/types
check/types:
	@uv run pyright griptape $(shell find docs -type f -path "*/src/*")
	
.PHONY: check/spell
check/spell:
	@uv run typos 
	
.PHONY: docs
docs: ## Build documentation.
	@uv run python -m mkdocs build --clean --strict 

.DEFAULT_GOAL := help
.PHONY: help
help: ## Print Makefile help text.
	@# Matches targets with a comment in the format <target>: ## <comment>
	@# then formats help output using these values.
	@grep -E '^[a-zA-Z_\/-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; \
		{printf "\033[36m%-12s\033[0m%s\n", $$1, $$2}'
