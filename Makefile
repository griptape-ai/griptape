version:
	@poetry version $(v)
	@git add pyproject.toml
	@git commit -m "Version bump v$$(poetry version -s)"

publish:
	@git merge --no-ff release-$$(poetry version -s)
	@git tag v$$(poetry version -s)
	@git push
	@git push --tags
	@poetry build
	@poetry publish
