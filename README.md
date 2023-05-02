# griptape

[![PyPI Version](https://img.shields.io/pypi/v/griptape.svg)](https://pypi.python.org/pypi/griptape)
[![Tests](https://github.com/griptape-ai/griptape/actions/workflows/tests.yml/badge.svg)](https://github.com/griptape-ai/griptape/actions/workflows/tests.yml)
[![Docs](https://readthedocs.org/projects/griptape/badge/)](https://griptape.readthedocs.io/)
[![Griptape Discord](https://dcbadge.vercel.app/api/server/gnWRz88eym?compact=true&style=flat)](https://discord.gg/gnWRz88eym)

**griptape** is a modular Python framework for LLM workflows, tools, memory, and data that enables developers to:

1. 🤖 Build **AI agents**, sequential **LLM pipelines** and sprawling **DAG workflows** for complex use cases.
2. ⛓️ Augment LLMs with **chain of thought** capabilities.
3. 🧰️ Integrate other services and functionality into LLMs as [tools](https://github.com/griptape-ai/griptape-tools) (e.g., calculators, web scrapers, spreadsheet editors, and API connectors); run tools in any environment (local, containerized, cloud, etc.); use tools directly in **griptape** or convert them into ramps abstractions, such as ChatGPT Plugins, LangChain tools, or Fixie.ai agents.
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

Second, configure an OpenAI client by [getting an API key](https://beta.openai.com/account/api-keys) and adding it to your environment as `OPENAI_API_KEY`. griptape uses [OpenAI Completions API](https://platform.openai.com/docs/guides/completion) to execute LLM prompts and to work with [LlamaIndex](https://gpt-index.readthedocs.io/en/latest/index.html) data structures.

With **griptape**, you can create *structures*, such as `Agents`, `Pipelines`, and `Workflows`, that are composed of different types of tasks. You can also define structures as JSON objects and load them into **griptape** dynamically. Let's define a simple two-task pipeline that uses tools:

```python
from decouple import config
from griptape.core import ToolLoader
from griptape.drivers import OpenAiPromptDriver, MemoryStorageDriver
from griptape.executors import LocalExecutor
from griptape.memory import Memory
from griptape.ramps import StorageRamp
from griptape.structures import Pipeline
from griptape.tasks import ToolkitTask, PromptTask
from griptape.tools import WebScraper

storage = StorageRamp(
    driver=MemoryStorageDriver()
)

scraper = WebScraper(
    ramps={
        "get_content": [storage]
    }
)

pipeline = Pipeline(
    memory=Memory(),
    tool_loader=ToolLoader(
        tools=[scraper],
        executor=LocalExecutor()
    )
)

pipeline.add_tasks(
    ToolkitTask(
        tool_names=[scraper.name]
    ),
    PromptTask(
        "Say the following in spanish: {{ input }}"
    )
)

result = pipeline.run("Give me a summary of https://en.wikipedia.org/wiki/Large_language_model")

print(result.output.value)


```

Boom! Our first LLM pipeline with two sequential tasks generated the following exchange:

```
Q: Give me a summary of https://en.wikipedia.org/wiki/Large_language_model
[chain of thought output... will vary depending on the model driver you're using]
A: Los modelos de lenguaje de gran tamaño son herramientas utilizadas para tareas de 
procesamiento del lenguaje natural, como detectar falsedades, completar oraciones y comprender 
el lenguaje. Algunos modelos notables incluyen BERT, GPT-2, GPT-3, GPT-Neo y GLaM. The Pile es 
un conjunto de datos extenso utilizado para el modelado del lenguaje. Estos modelos han sido 
desarrollados e investigados en trabajos como TruthfulQA, HellaSwag y BERT: Pre-entrenamiento 
de transformadores bidireccionales profundos para la comprensión del lenguaje.
```

## Versioning

**griptape** is in early development and its APIs and documentation are subject to change. Until we stabilize the API and release version 1.0.0, we will use minor versions (i.e., x.Y.z) to introduce features and breaking features, and patch versions (i.e., x.y.Z) for bug fixes.

## Contributing

Contributions in the form of bug reports, feature ideas, or pull requests are super welcome! Take a look at the current issues and if you'd like to help please submit a pull request with some tests.

## License

**griptape** is available under the Apache 2.0 License.
