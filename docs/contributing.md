# Contributing

Thank you for considering contributing to Griptape documentation! Before you start, please read our [contributing guidelines](https://github.com/griptape-ai/griptape/blob/main/CONTRIBUTING.md).

## Getting Started

Griptape docs are built using [MkDocs](https://squidfunk.github.io/mkdocs-material/getting-started/).
Dependencies are managed using [uv](https://docs.astral.sh/uv/).

To contribute to Griptape docs, install the `docs` extra with:

`uv install --group docs`

Then serve the documentation locally with:

`uv run mkdocs serve`

You should see something similar to the following:

```
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.19 seconds
INFO     -  [09:28:33] Watching paths for changes: 'docs', 'mkdocs.yml'
INFO     -  [09:28:33] Serving on http://127.0.0.1:8000/
INFO     -  [09:28:37] Browser connected: http://127.0.0.1:8000/
```
