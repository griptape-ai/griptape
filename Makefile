.PHONY: install
install: ## Install all dependencies.
	@make install/all

.PHONY: install/core
install/core: ## Install core dependencies.
	@poetry install

.PHONY: install/all
install/all: ## Install all dependencies.
	@poetry install --with dev --with test --with docs --all-extras
	@poetry run pre-commit install

.PHONY: install/dev
install/dev: ## Install dev dependencies.
	@poetry install --with dev

.PHONY: install/test
install/test: ## Install test dependencies.
	@poetry install --with test

.PHONY: test  ## Run all tests.
test: test/unit test/integration

.PHONY: test/unit
test/unit: ## Run unit tests.
	@poetry run pytest -n auto tests/unit

.PHONY: test/unit/%
test/unit/%: ## Run specific unit tests.
	@poetry run pytest -n auto tests/unit -k $*

.PHONY: test/unit/coverage
test/unit/coverage:
	@poetry run pytest -n auto --cov=griptape tests/unit

.PHONY: test/integration
test/integration:
	@poetry run pytest -n auto tests/integration/test_code_blocks.py

.PHONY: lint
lint: ## Lint project.
	@poetry run ruff check --fix

.PHONY: format
format: ## Format project.
	@poetry run ruff format
	@poetry run mdformat .github/ docs/

.PHONY: check
check: check/format check/lint check/types check/spell ## Run all checks.

.PHONY: check/format
check/format:
	@poetry run ruff format --check
	@poetry run mdformat --check .github/ docs/

.PHONY: check/lint
check/lint:
	@poetry run ruff check

.PHONY: check/types
check/types:
	@poetry run pyright griptape $(shell find docs -type f -path "*/src/*")
	
.PHONY: check/spell
check/spell:
	@poetry run typos 
	
.PHONY: docs
docs: ## Build documentation.
	@poetry run python -m mkdocs build --clean --strict 

.DEFAULT_GOAL := help
.PHONY: help
help: ## Print Makefile help text.
	@# Matches targets with a comment in the format <target>: ## <comment>
	@# then formats help output using these values.
	@grep -E '^[a-zA-Z_\/-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; \
		{printf "\033[36m%-12s\033[0m%s\n", $$1, $$2}'
