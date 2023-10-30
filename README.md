# griptape

[![PyPI Version](https://img.shields.io/pypi/v/griptape.svg)](https://pypi.python.org/pypi/griptape)
[![Tests](https://github.com/griptape-ai/griptape/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/griptape-ai/griptape/actions/workflows/unit-tests.yml)
[![Docs](https://readthedocs.org/projects/griptape/badge/)](https://griptape.readthedocs.io/)
[![Griptape Discord](https://dcbadge.vercel.app/api/server/gnWRz88eym?compact=true&style=flat)](https://discord.gg/gnWRz88eym)

**Griptape** is a modular Python framework for building AI-powered applications that connect securely to your enterprise data and APIs. It offers developers the ability to maintain control and flexibility at every step.

**Build AI Apps**: Easily compose apps in Python with modular structures and ready-made tools. Use built-in drivers to connect to whichever LLMs and data stores you choose.

**Control Data Access**: Connect securely to data sources with granular access controls, ensuring LLMs stay focused on the information that matters.

**Scale With Your Workload**: Easily deploy and run apps in the cloud, where your data lives. Process data ahead of time or vectorize it on the fly.

Using Griptape, you can securely integrate with your internal data stores and APIs. You get to control what data goes into the prompt, and what the LLM is allowed to do with it. 

## Documentation

Please refer to [Griptape Docs](https://docs.griptape.ai/) for:

- Getting started guides. 
- Core concepts and design overviews.
- Examples.
- Contribution guidelines.

Please check out [Griptape Trade School](https://learn.griptape.ai/) for free online courses.

## Quick Start

First, install **griptape**:

```
pip install griptape -U
```

Second, configure an OpenAI client by [getting an API key](https://beta.openai.com/account/api-keys) and adding it to your environment as `OPENAI_API_KEY`. By default, Griptape uses [OpenAI Completions API](https://platform.openai.com/docs/guides/completion) to execute LLM prompts.

With Griptape, you can create *structures*, such as `Agents`, `Pipelines`, and `Workflows`, that are composed of different types of tasks. Let's build a simple creative agent that dynamically uses two tools with shared short-term memory.

```python
from griptape.structures import Agent
from griptape.tools import WebScraper

agent = Agent(
    tools=[WebScraper()]
)

agent.run(
    "based on https://www.griptape.ai/, tell me what Griptape is"
)
```

And here is the output:

> Q: based on https://www.griptape.ai/, tell me what Griptape is  
> A: Griptape is an opinionated Python framework that enables developers to fully harness the potential of LLMs while enforcing strict trust boundaries, schema validation, and activity-level permissions. It offers developers the ability to build AI systems that operate across two dimensions: predictability and creativity. Griptape can be used to create conversational and autonomous agents.

During the run, the Griptape agent loaded a webpage with a **tool**, stored its full content in the **short-term memory**, and finally queried it to answer the original question. The important thing to note here is that no matter how big the webpage is it can never blow up the prompt token limit because the full content never goes back to the main prompt.

[Check out our docs](https://docs.griptape.ai/griptape-framework/structures/prompt-drivers/) to learn more about how to use Griptape with other LLM providers like Anthropic, Claude, Hugging Face, and Azure.

## Versioning

Griptape is in constant development and its APIs and documentation are subject to change. Until we stabilize the API and release version 1.0.0, we will use minor versions (i.e., x.Y.z) to introduce features and breaking features, and patch versions (i.e., x.y.Z) for bug fixes.

## Contributing

Thank you for considering contributing to Griptape! Before you start, please read the following guidelines.

### Submitting Issues

If you have identified a bug, want to propose a new feature, or have a question, please submit an issue. Before submitting a new issue, please check the existing issues to ensure it hasn't been reported or discussed before.

### Submitting Pull Requests

We welcome and encourage pull requests. To streamline the process, please follow these guidelines:

1. **Existing Issues:** Please submit pull requests only for existing issues. If you want to work on new functionality or fix a bug that hasn't been addressed yet, please first submit an issue. This allows the Griptape team to internally process the request and provide a public response.

2. **Branch:** Submit all pull requests to the `dev` branch. This helps us manage changes and integrate them smoothly.

3. **Unit Tests:** Ensure that your pull request passes all existing unit tests. Additionally, if you are introducing new code, please include new unit tests to validate its functionality.

4. **Documentation:** Every pull request must include a corresponding pull request in the [docs repository](https://github.com/griptape-ai/griptape-docs) or explicitly explain why a documentation update is not required. Documentation is crucial for maintaining a comprehensive and user-friendly project.

## License

Griptape is available under the Apache 2.0 License.
