# griptape

[![PyPI Version](https://img.shields.io/pypi/v/griptape.svg)](https://pypi.python.org/pypi/griptape)
[![Tests](https://github.com/griptape-ai/griptape/actions/workflows/tests.yml/badge.svg)](https://github.com/griptape-ai/griptape/actions/workflows/tests.yml)
[![Docs](https://readthedocs.org/projects/griptape/badge/)](https://griptape.readthedocs.io/)
[![Griptape Discord](https://dcbadge.vercel.app/api/server/gnWRz88eym?compact=true&style=flat)](https://discord.gg/gnWRz88eym)

**griptape** is a modular Python framework for LLM workflows, tools, memory, and data that enables developers to:

1. 🤖 Build **AI agents**, sequential **LLM pipelines** and sprawling **DAG workflows** for complex use cases.
2. ⛓️ Augment LLMs with **chain of thought** capabilities.
3. 🧰️ Integrate other services and functionality into LLMs as [tools](https://github.com/griptape-ai/griptape-tools) (e.g., calculators, web scrapers, spreadsheet editors, and API connectors); run tools in any environment (local, containerized, cloud, etc.); and wrap tools with off prompt data storage that prevents LLMs from accessing your data directly.
4. 💾 Add **memory** to AI pipelines for context preservation and summarization.

## Documentation

Please refer to [Griptape Docs](https://griptape.readthedocs.io) for:

- Getting started guides. 
- Core concepts and design overviews.
- Examples.
- Contribution guidelines.

## Quick Start

First, install **griptape** and **griptape-tools**:

```
pip install griptape griptape-tools -U
```

Second, configure an OpenAI client by [getting an API key](https://beta.openai.com/account/api-keys) and adding it to your environment as `OPENAI_API_KEY`. **griptape** uses [OpenAI Completions API](https://platform.openai.com/docs/guides/completion) to execute LLM prompts.

With **griptape**, you can create *structures*, such as `Agents`, `Pipelines`, and `Workflows`, that are composed of different types of tasks. Let's define a simple two-task pipeline that uses several tools and ramps:

```python
from griptape.memory import Memory
from griptape.ramps import TextStorageRamp, BlobStorageRamp
from griptape.structures import Pipeline
from griptape.tasks import ToolkitTask, PromptTask
from griptape.tools import WebScraper, TextProcessor, FileManager

# Ramps enable LLMs to store and manipulate data without ever looking at it directly.
text_storage = TextStorageRamp()
blob_storage = BlobStorageRamp()

# Connect a web scraper to load web pages.
web_scraper = WebScraper(
    ramps={
        "get_content": [text_storage]
    }
)

# TextProcessor enables LLMs to summarize and query text.
text_processor = TextProcessor(
    ramps={
        "summarize": [text_storage],
        "query": [text_storage]
    }
)

# File manager can load and store files locally.
file_manager = FileManager(
    ramps={
        "load": [blob_storage],
        "save": [text_storage, blob_storage]
    }
)

# Pipelines represent sequences of tasks.
pipeline = Pipeline(
    memory=Memory()
)

pipeline.add_tasks(
    # Load up the first argument from `pipeline.run`.
    ToolkitTask(
        "{{ args[0] }}",
        tools=[web_scraper, text_processor, file_manager]
    ),
    # Augment `input` from the previous task.
    PromptTask(
        "Say the following in spanish: {{ input }}"
    )
)

result = pipeline.run("Load https://griptape.readthedocs.io, summarize it, and store it in griptape.txt")

print(result.output.to_text())
```

Boom! Our first LLM pipeline with two sequential tasks generated the following exchange:

```
Q: Load https://griptape.readthedocs.io, summarize it, and store it in griptape.txt
A: El contenido de https://griptape.readthedocs.io ha sido resumido y almacenado en griptape.txt.
```

During the run, **griptape** prompted the LLM to load a webpage, store its content in temporary memory, summarize the content, and, finally, save it `griptape.txt`.

## Versioning

**griptape** is in early development and its APIs and documentation are subject to change. Until we stabilize the API and release version 1.0.0, we will use minor versions (i.e., x.Y.z) to introduce features and breaking features, and patch versions (i.e., x.y.Z) for bug fixes.

## Contributing

Contributions in the form of bug reports, feature ideas, or pull requests are super welcome! Take a look at the current issues and if you'd like to help please submit a pull request with some tests.

## License

**griptape** is available under the Apache 2.0 License.
