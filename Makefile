.PHONY: version
version: ## Bump version and push to release branch. ex: make version v=0.1.0
	@poetry version $(v)
	@git add pyproject.toml
	@git commit -m "Version bump v$$(poetry version -s)"
	@git push origin release/v$$(poetry version -s)

.PHONY: publish
publish: ## Publish version to Git and PyPI.
	@git tag v$$(poetry version -s)
	@git push --tags
	@poetry build
	@poetry publish

.DEFAULT_GOAL := help
.PHONY: help
help: ## Print Makefile help text.
	@grep -E '^[a-zA-Z_\/-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; \
		{printf "\033[36m%-20s\033[0m%s\n", $$1, $$2}'
