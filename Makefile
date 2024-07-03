.PHONY: version
version: ## Bump version and push to release branch.
	@poetry version $(v)
	@git add pyproject.toml
	@git commit -m "Version bump v$$(poetry version -s)"
	@git push origin release/v$$(poetry version -s)

.PHONY: publish
publish: ## Push git tag and publish version to PyPI.
	@git tag $$(poetry version -s)
	@git push --tags
	@poetry build
	@poetry publish

.PHONY: install
install: ## Install all dependencies.
	@poetry install --with dev --with test --with docs --all-extras
	@poetry run pre-commit install

.PHONY: test  ## Run all tests.
test: test/unit test/integration

.PHONY: test/unit
test/unit: ## Run unit tests.
	@poetry run pytest -n auto tests/unit

.PHONY: test/unit/coverage
test/unit/coverage:
	@poetry run pytest -n auto --cov=griptape tests/unit

.PHONY: test/integration
test/integration:
	@poetry run pytest -n auto tests/integration/test_code_blocks.py

.PHONY: lint
lint: ## Lint project.
	@poetry run ruff check --fix griptape/

.PHONY: format
format: ## Format project.
	@poetry run ruff format .

.PHONY: check
check: check/format check/lint check/types check/spell ## Run all checks.

.PHONY: check/format
check/format:
	@poetry run ruff format --check griptape/

.PHONY: check/lint
check/lint:
	@poetry run ruff check griptape/

.PHONY: check/types
check/types:
	@poetry run pyright griptape/
	
.PHONY: check/spell
check/spell:
	@poetry run typos 
	
.PHONY: docs
docs: ## Build documentation.
	@poetry run mkdocs build

.DEFAULT_GOAL := help
.PHONY: help
help: ## Print Makefile help text.
	@# Matches targets with a comment in the format <target>: ## <comment>
	@# then formats help output using these values.
	@grep -E '^[a-zA-Z_\/-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; \
		{printf "\033[36m%-12s\033[0m%s\n", $$1, $$2}'
