version:
	@poetry version $(v)
	@git add pyproject.toml
	@git commit -m "Version bump v$$(poetry version -s)"
	@git push origin release/v$$(poetry version -s)

publish:
	@git tag v$$(poetry version -s)
	@git push --tags
	@poetry build
	@poetry publish
