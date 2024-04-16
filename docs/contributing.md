# Contributing

Thank you for considering contributing to Griptape documentation! Before you start, please read the following guidelines.

## Submitting Issues

If you have identified a documentation issue, want to propose new documentation, or have a question, please submit an issue through our public [issue tracker](https://github.com/griptape-ai/griptape/issues). Before submitting a new issue, please check the existing issues to ensure it hasn't been reported or discussed before.

## Submitting Pull Requests

We welcome and encourage pull requests. To streamline the process, please follow these guidelines:

1. **Existing Issues:** Please submit pull requests only for existing issues. If you want to add new documentation or fix a documentation issue that hasn't been addressed yet, please first submit an issue. This allows the Griptape team to internally process the request and provide a public response.

2. **Branch:** Submit all pull requests to the `dev` branch. This helps us manage changes and integrate them smoothly.

## Getting Started
Griptape docs are built using [MkDocs](https://squidfunk.github.io/mkdocs-material/getting-started/). Dependencies are managed using [Poetry](https://python-poetry.org/).

To contribute to Griptape docs, install the `docs` extra with:

```poetry install --with docs```

Then serve the documentation locally with:

```poetry run mkdocs serve```

You should see something similar to the following: 

```
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.19 seconds
INFO     -  [09:28:33] Watching paths for changes: 'docs', 'mkdocs.yml'
INFO     -  [09:28:33] Serving on http://127.0.0.1:8000/
INFO     -  [09:28:37] Browser connected: http://127.0.0.1:8000/
```
