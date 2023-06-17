# griptape

[![PyPI Version](https://img.shields.io/pypi/v/griptape.svg)](https://pypi.python.org/pypi/griptape)
[![Tests](https://github.com/griptape-ai/griptape/actions/workflows/tests.yml/badge.svg)](https://github.com/griptape-ai/griptape/actions/workflows/tests.yml)
[![Docs](https://readthedocs.org/projects/griptape/badge/)](https://griptape.readthedocs.io/)
[![Griptape Discord](https://dcbadge.vercel.app/api/server/gnWRz88eym?compact=true&style=flat)](https://discord.gg/gnWRz88eym)

**Griptape** offers developers the ability to build AI systems that operate across two dimensions: predictability and creativity.

For **predictability**, software structures like sequential pipelines and directed acyclic graphs (DAGs) are enforced. **Creativity**, on the other hand, is facilitated by safely prompting LLMs with [tools](https://github.com/griptape-ai/griptape-tools) that connect to external APIs and data sources. Developers can move between these two dimensions according to their use case.

## Documentation

Please refer to [Griptape Docs](https://docs.griptape.ai/) for:

- Getting started guides. 
- Core concepts and design overviews.
- Examples.
- Contribution guidelines.

## Quick Start

First, install **griptape** and **griptape-tools**:

```
pip install griptape griptape-tools -U
```

Second, configure an OpenAI client by [getting an API key](https://beta.openai.com/account/api-keys) and adding it to your environment as `OPENAI_API_KEY`. By default, Griptape uses [OpenAI Completions API](https://platform.openai.com/docs/guides/completion) to execute LLM prompts.

With Griptape, you can create *structures*, such as `Agents`, `Pipelines`, and `Workflows`, that are composed of different types of tasks. Let's build a simple creative agent that dynamically uses two tools with shared memory.

```python
from griptape.memory.tool import TextToolMemory
from griptape.structures import Agent
from griptape.tools import WebScraper
from griptape.utils import Conversation


"""
Define memory to be shared between tools.
"""
memory = TextToolMemory()

"""
WebScraper enables LLMs to load web pages.
"""
web_scraper = WebScraper(
    output_memory={"get_content": [memory]}
)

"""
Agents can use multiple tools to creatively solve problems
"""
agent = Agent(
    tools=[web_scraper]
)

agent.run(
    "based on https://www.griptape.ai/, tell me what Griptape is"
)

print(
    Conversation(agent.memory)
)
```

And here is the output:

> Q: based on https://www.griptape.ai/, tell me what Griptape is  
> A: Griptape is an opinionated Python framework that enables developers to fully harness the potential of LLMs while enforcing strict trust boundaries, schema validation, and activity-level permissions. It offers developers the ability to build AI systems that operate across two dimensions: predictability and creativity. Griptape can be used to create conversational and autonomous agents.

During the run, the Griptape agent loaded a webpage, stored its full content in temporary memory, and finally queried it to answer the original question.

## Versioning

Griptape is in early development and its APIs and documentation are subject to change. Until we stabilize the API and release version 1.0.0, we will use minor versions (i.e., x.Y.z) to introduce features and breaking features, and patch versions (i.e., x.y.Z) for bug fixes.

## Contributing

Contributions in the form of bug reports, feature ideas, or pull requests are super welcome! Take a look at the current issues and if you'd like to help please submit a pull request with some tests.

## License

Griptape is available under the Apache 2.0 License.
