# griptape

[![PyPI Version](https://img.shields.io/pypi/v/griptape.svg)](https://pypi.python.org/pypi/griptape)
[![Tests](https://github.com/griptape-ai/griptape/actions/workflows/tests.yml/badge.svg)](https://github.com/griptape-ai/griptape/actions/workflows/tests.yml)
[![Docs](https://readthedocs.org/projects/griptape/badge/)](https://griptape.readthedocs.io/)
[![Griptape Discord](https://dcbadge.vercel.app/api/server/gnWRz88eym?compact=true&style=flat)](https://discord.gg/gnWRz88eym)

**griptape** is a modular Python framework for LLM workflows, tools, memory, and data that enables developers to:

1. 🤖 Build **AI agents**, sequential **LLM pipelines** and sprawling **DAG workflows** for complex use cases.
2. ⛓️ Augment LLMs with **chain of thought** capabilities.
3. 🧰️ Integrate other services and functionality into LLMs as [tools](https://github.com/griptape-ai/griptape-tools) (e.g., calculators, web scrapers, spreadsheet editors, and API connectors); run tools in any environment (local, containerized, cloud, etc.); use tools directly in **griptape** or convert them into middleware abstractions, such as ChatGPT Plugins, LangChain tools, or Fixie.ai agents.
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

With **griptape**, you can create *structures*, such as `Agents`, `Pipelines`, and `Workflows`, that are composed of different types of tasks. You can also define structures as JSON objects and load them into **griptape** dynamically. Let's define a simple two-step pipeline that uses tools:

```python
from decouple import config
from griptape.tools import WebScraper, Calculator
from griptape import utils
from griptape.memory import Memory
from griptape.tasks import PromptTask, ToolkitTask
from griptape.structures import Pipeline
from griptape.utils import ToolLoader

scraper = WebScraper(
    openai_api_key=config("OPENAI_API_KEY")
)
calculator = Calculator()

pipeline = Pipeline(
    memory=Memory(),
    tool_loader=ToolLoader(
        tools=[calculator, scraper]
    )
)

pipeline.add_tasks(
    ToolkitTask(
        tool_names=[calculator.name, scraper.name]
    ),
    PromptTask(
        "Say the following like a pirate: {{ input }}"
    )
)

pipeline.run("Give me a summary of https://en.wikipedia.org/wiki/Large_language_model")

print(utils.Conversation(pipeline.memory).to_string())

```

Boom! Our first multistep LLM pipeline with memory that used tools generated a conversation:

> Q: Give me a summary of https://en.wikipedia.org/wiki/Large_language_model  
> A: Arr, me hearties! Large language models have been developed and set sail since 2018, includin' BERT, GPT-2, GPT-3 [...]

## Versioning

**griptape** is in early development and its APIs and documentation are subject to change. Until we stabilize the API and release version 1.0.0, we will use minor versions (i.e., x.Y.z) to introduce features and breaking features, and patch versions (i.e., x.y.Z) for bug fixes.

## Contributing

Contributions in the form of bug reports, feature ideas, or pull requests are super welcome! Take a look at the current issues and if you'd like to help please submit a pull request with some tests.

## License

**griptape** is available under the Apache 2.0 License.
