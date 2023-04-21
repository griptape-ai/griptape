# griptape

[![PyPI Version](https://img.shields.io/pypi/v/griptape.svg)](https://pypi.python.org/pypi/griptape)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/gitbucket/gitbucket/blob/master/LICENSE)
[![Griptape Discord](https://dcbadge.vercel.app/api/server/gnWRz88eym?compact=true&style=flat)](https://discord.gg/gnWRz88eym)

**griptape** is a modular Python framework for LLM workflows, tools, memory, and data that enables developers to:

1. 🚰 Build sequential **LLM pipelines** and sprawling **DAG workflows** for complex use cases.
2. 🧰️ Augment LLMs with **chain of thought** capabilities and integrate **external tools**, such as calculators, web search, spreadsheet editors, and API connectors.
3. 💾 Add **memory** to AI pipelines for context preservation and summarization.

## Main Packages

### [griptape-flow](https://github.com/griptape-ai/griptape-flow)
[![Tests](https://github.com/griptape-ai/griptape-flow/actions/workflows/tests.yml/badge.svg)](https://github.com/griptape-ai/griptape-flow/actions/workflows/tests.yml)
[![PyPI Version](https://img.shields.io/pypi/v/griptape-flow.svg)](https://pypi.python.org/pypi/griptape-flow)
[![Docs](https://readthedocs.org/projects/griptape/badge/)](https://griptape.readthedocs.io/en/latest/griptape_flow/)

Build LLM workflows and pipelines with memory, rules, and chain of thought reasoning.

---

### [griptape-core](https://github.com/griptape-ai/griptape-core)
[![Tests](https://github.com/griptape-ai/griptape-core/actions/workflows/tests.yml/badge.svg)](https://github.com/griptape-ai/griptape-core/actions/workflows/tests.yml)
[![PyPI Version](https://img.shields.io/pypi/v/griptape-core.svg)](https://pypi.python.org/pypi/griptape-core)
[![Docs](https://readthedocs.org/projects/griptape/badge/)](https://griptape.readthedocs.io/en/latest/griptape_core/)

Integrate other services and functionality into LLMs as tools; run tools in any environment (local, containerized, cloud, etc.); convert tools into underlying middleware abstractions, such as ChatGPT Plugins, LangChain tools, and Fixie.ai agents.

---

### [griptape-tools](https://github.com/griptape-ai/griptape-tools)
[![Tests](https://github.com/griptape-ai/griptape-tools/actions/workflows/tests.yml/badge.svg)](https://github.com/griptape-ai/griptape-tools/actions/workflows/tests.yml)
[![PyPI Version](https://img.shields.io/pypi/v/griptape-tools.svg)](https://pypi.python.org/pypi/griptape-tools)
[![Docs](https://readthedocs.org/projects/griptape/badge/)](https://griptape.readthedocs.io/en/latest/griptape_tools/overview/)

Official Griptape tools registry.

## Documentation

Please refer to [Griptape Docs](https://griptape.readthedocs.io) for:

- Getting started guides. 
- Core concepts and design overviews.
- Examples.
- Contribution guidelines.

## Quick Start

First, install griptape that includes all core modules:

```
pip install griptape -U
```

Second, configure an OpenAI client by [getting an API key](https://beta.openai.com/account/api-keys) and adding it to your environment as `OPENAI_API_KEY`. griptape uses [OpenAI Completions API](https://platform.openai.com/docs/guides/completion) to execute LLM prompts and to work with [LlamaIndex](https://gpt-index.readthedocs.io/en/latest/index.html) data structures.

With griptape, you can create *structures*, such as `Pipelines` and `Workflows`, that are composed of different types of steps. You can also define structures as JSON objects and load them into griptape dynamically. Let's define a simple two-step pipeline that uses tools:

```python
from decouple import config
from griptape.tools import WebScraper, Calculator
from griptape.flow import utils
from griptape.flow.memory import PipelineMemory
from griptape.flow.steps import PromptStep, ToolkitStep
from griptape.flow.structures import Pipeline
from griptape.flow.utils import ToolLoader


scraper = WebScraper(
    openai_api_key=config("OPENAI_API_KEY")
)
calculator = Calculator()

pipeline = Pipeline(
    memory=PipelineMemory(),
    tool_loader=ToolLoader(
        tools=[calculator, scraper]
    )
)

pipeline.add_steps(
    ToolkitStep(
        tool_names=[calculator.name, scraper.name]
    ),
    PromptStep(
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

**griptape** is in early development and its APIs and documentation are subject to change. Until we stabilize the API and release version 1.0.0, we will use minor versions (i.e., x.Y.z) to introduce breaking features and patch versions (i.e., x.y.Z) for bug fixes.

## Contributing

Contributions in the form of bug reports, feature ideas, or pull requests are super welcome! Take a look at the current issues and if you'd like to help please submit a pull request with some tests.

## License

**griptape** is available under the Apache 2.0 License.
