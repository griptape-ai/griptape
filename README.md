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

Second, configure an OpenAI client by [getting an API key](https://platform.openai.com/account/api-keys) and adding it to your environment as `OPENAI_API_KEY`. By default, Griptape uses [OpenAI Chat Completions API](https://platform.openai.com/docs/guides/gpt/chat-completions-api) to execute LLM prompts.

With Griptape, you can create *structures*, such as `Agents`, `Pipelines`, and `Workflows`, that are composed of different types of tasks. Let's build a simple creative agent that dynamically uses two tools with shared short-term memory.

```python
from griptape.structures import Agent
from griptape.tools import WebScraper, FileManager


agent = Agent(
    input_template="Load {{ args[0] }}, summarize it, and store it in a file called {{ args[1] }}.", 
    tools=[WebScraper(), FileManager()]
)
agent.run("https://griptape.ai", "griptape.txt")
```

And here is the output:
```
INFO     ToolkitTask 51b46eff74a64133a1b6d47c630f1db5
         Input: Load https://www.griptape.ai, summarize it, and store it in a file called griptape.txt
INFO     Subtask 13a7772aea2840259c521f6dcaf8a7b0
         Thought: To complete this task, I need to first load the webpage using the WebScraper tool's get_content activity. Then, I will summarize the content using the TextToolMemory's summarize activity. Finally, I will store the summarized content in a file
         named "griptape.txt" using the FileManager tool's save_content_to_file activity.
         Action: {"type": "tool", "name": "WebScraper", "activity": "get_content", "input": {"values": {"url": "https://www.griptape.ai"}}}
INFO     Subtask 13a7772aea2840259c521f6dcaf8a7b0
         Observation: Output of "WebScraper.get_content" was stored in memory with memory_name "TextToolMemory" and artifact_namespace "a84ab9258aa540f99607c5df73da2d2d"
INFO     Subtask 905bc561be3f4ff48894d8984814a44f
         Thought: Now that the webpage content is stored in memory, I can use the TextToolMemory's summarize activity to summarize the content.
         Action: {"type": "memory", "name": "TextToolMemory", "activity": "summarize", "input": {"values": {"memory_name": "TextToolMemory", "artifact_namespace": "a84ab9258aa540f99607c5df73da2d2d"}}}
INFO     Subtask 905bc561be3f4ff48894d8984814a44f
         Observation: The text describes Griptape, an open-source Python framework and managed cloud platform for building and deploying AI applications for enterprise use. Griptape allows users to easily create AI-powered agents, compose event-driven pipelines,
         and orchestrate complex workflows. It provides tools for connecting to data sources securely and controlling data access. The text also provides examples of creating a Griptape agent, pipeline, and workflow. Griptape Cloud is mentioned as a managed
         platform for running AI agents, pipelines, and workflows. The text concludes by offering customers the opportunity to contact Griptape for further information and assistance.
INFO     Subtask 459f35e5af4e49f7ac87a5989447dcb4
         Thought: Now that I have summarized the content of the webpage, I can store this summary in a file named "griptape.txt" using the FileManager tool's save_content_to_file activity.
         Action: {"type": "tool", "name": "FileManager", "activity": "save_content_to_file", "input": {"values": {"path": "griptape.txt", "content": "The text describes Griptape, an open-source Python framework and managed cloud platform for building and deploying
         AI applications for enterprise use. Griptape allows users to easily create AI-powered agents, compose event-driven pipelines, and orchestrate complex workflows. It provides tools for connecting to data sources securely and controlling data access. The
         text also provides examples of creating a Griptape agent, pipeline, and workflow. Griptape Cloud is mentioned as a managed platform for running AI agents, pipelines, and workflows. The text concludes by offering customers the opportunity to contact
         Griptape for further information and assistance."}}}
INFO     Subtask 459f35e5af4e49f7ac87a5989447dcb4
         Observation: saved successfully
INFO     ToolkitTask 51b46eff74a64133a1b6d47c630f1db5
         Output: The summarized content of the webpage "https://www.griptape.ai" has been successfully stored in a file named "griptape.txt".
```

During the run, the Griptape Agent loaded a webpage with a **Tool**, stored its full content in **Tool Memory**, queried it to answer the original question, and finally saved the answer to a file.
The important thing to note here is that no matter how big the webpage is it can never blow up the prompt token limit because the full content never goes back to the main prompt.

[Check out our docs](https://docs.griptape.ai/griptape-framework/structures/prompt-drivers/) to learn more about how to use Griptape with other LLM providers like Anthropic, Claude, Hugging Face, and Azure.

## Versioning

Griptape is in constant development and its APIs and documentation are subject to change. Until we stabilize the API and release version 1.0.0, we will use minor versions (i.e., x.Y.z) to introduce features and breaking features, and patch versions (i.e., x.y.Z) for bug fixes.

## Contributing

Thank you for considering contributing to Griptape! Before you start, please read the following guidelines.

### Submitting Issues

If you have identified a bug, want to propose a new feature, or have a question, please submit an issue through our public [issue tracker](https://github.com/griptape-ai/griptape/issues). Before submitting a new issue, please check the existing issues to ensure it hasn't been reported or discussed before.

### Submitting Pull Requests

We welcome and encourage pull requests. To streamline the process, please follow these guidelines:

1. **Existing Issues:** Please submit pull requests only for existing issues. If you want to work on new functionality or fix a bug that hasn't been addressed yet, please first submit an issue. This allows the Griptape team to internally process the request and provide a public response.

2. **Branch:** Submit all pull requests to the `dev` branch. This helps us manage changes and integrate them smoothly.

3. **Unit Tests:** Ensure that your pull request passes all existing unit tests. Additionally, if you are introducing new code, please include new unit tests to validate its functionality.

4. **Documentation:** Every pull request must include a corresponding pull request in the [docs repository](https://github.com/griptape-ai/griptape-docs) or explicitly explain why a documentation update is not required. Documentation is crucial for maintaining a comprehensive and user-friendly project.

## License

Griptape is available under the Apache 2.0 License.
