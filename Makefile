.PHONY: version
version: ## Bump version and push to release branch.
	@poetry version $(v)
	@git add pyproject.toml
	@git commit -m "Version bump v$$(poetry version -s)"
	@git push origin release/v$$(poetry version -s)

.PHONY: publish
publish: ## Push git tag and publish version to PyPI.
	@git tag v$$(poetry version -s)
	@git push --tags
	@poetry build
	@poetry publish

.DEFAULT_GOAL := help
.PHONY: help
help: ## Print Makefile help text.
	@# Matches targets with a comment in the format <target>: ## <comment>
	@# then formats help output using these values.
	@grep -E '^[a-zA-Z_\/-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; \
		{printf "\033[36m%-12s\033[0m%s\n", $$1, $$2}'
