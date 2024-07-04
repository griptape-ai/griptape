![Griptape](https://assets-global.website-files.com/65d658559223871198e78bca/65fb8d85c1ab3c9b858ab18a_Griptape%20logo%20dark.svg)

[![PyPI Version](https://img.shields.io/pypi/v/griptape.svg)](https://pypi.python.org/pypi/griptape)
[![Tests](https://github.com/griptape-ai/griptape/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/griptape-ai/griptape/actions/workflows/unit-tests.yml)
[![Docs](https://readthedocs.org/projects/griptape/badge/)](https://griptape.readthedocs.io/)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/github/griptape-ai/griptape/graph/badge.svg?token=HUBqUpl3NB)](https://codecov.io/github/griptape-ai/griptape)
[![Griptape Discord](https://dcbadge.vercel.app/api/server/gnWRz88eym?compact=true&style=flat)](https://discord.gg/griptape)

Griptape is a modular Python framework for building AI-powered applications that securely connect to your enterprise data and APIs. It offers developers the ability to maintain control and flexibility at every step.


## 🛠️ Core Components

### 🏗️ Structures

- 🤖 **Agents** consist of a single Task.
- 🔄 **Pipelines** organize a sequence of Tasks so that the output from one Task may flow into the next.
- 🌐 **Workflows** configure Tasks to operate in parallel.

### 📝 Tasks

Tasks are the core building blocks within Structures, enabling interaction with Engines, Tools, and other Griptape components.

### 🔧 Tools

Tools provide capabilities for LLMs to interact with data and services. Griptape includes a variety of built-in Tools, and makes it easy to create custom Tools.

### 🧠 Memory

- 💬 **Conversation Memory** enables LLMs to retain and retrieve information across interactions.
- 🗃️ **Task Memory** keeps large or sensitive Task outputs off the prompt that is sent to the LLM.
- 📊 **Meta Memory** enables passing in additional metadata to the LLM, enhancing the context and relevance of the interaction.

### 🚗 Drivers

Drivers facilitate interactions with external resources and services:

- 🗣️ **Prompt Drivers** manage textual interactions with LLMs.
- 🔢 **Embedding Drivers** generate vector embeddings from textual inputs.
- 💾 **Vector Store Drivers** manage the storage and retrieval of embeddings.
- 🎨 **Image Generation Drivers** create images from text descriptions.
- 🔎 **Image Query Drivers** query images from text queries.
- 💼 **SQL Drivers** interact with SQL databases.
- 🌐 **Web Scraper Drivers** extract information from web pages.
- 🧠 **Conversation Memory Drivers** manage the storage and retrieval of conversational data.

### 🚂 Engines

Engines wrap Drivers and provide use-case-specific functionality:

- 📊 **RAG Engine** is an abstraction for implementing modular Retrieval Augmented Generation (RAG) pipelines.
- 🛠️ **Extraction Engines** extract JSON or CSV data from unstructured text.
- 📝 **Summary Engines** generate summaries from textual content.
- 🖼️ **Image Generation Engines** generate images from textual descriptions.
- 🔎 **Image Query Engines** query images based on textual prompts.

### 📦 Additional Components

- 📐 **Rulesets** steer LLM behavior with minimal prompt engineering.
- 🔄 **Loaders** load data from various sources.
- 🏺 **Artifacts** allow for passing data of different types between Griptape components.
- ✂️ **Chunkers** segment texts into manageable pieces for diverse text types.
- 🔢 **Tokenizers**  count the number of tokens in a text to not exceed LLM token limits.

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
pip install "griptape[all]" -U
```

Second, configure an OpenAI client by [getting an API key](https://platform.openai.com/account/api-keys) and adding it to your environment as `OPENAI_API_KEY`. By default, Griptape uses [OpenAI Chat Completions API](https://platform.openai.com/docs/guides/gpt/chat-completions-api) to execute LLM prompts.

With Griptape, you can create Structures, such as Agents, Pipelines, and Workflows, composed of different types of Tasks. Let's build a simple creative Agent that dynamically uses three tools and moves the data around in Task Memory.

```python
from griptape.structures import Agent
from griptape.tools import WebScraper, FileManager, TaskMemoryClient

agent = Agent(
    input="Load {{ args[0] }}, summarize it, and store it in a file called {{ args[1] }}.",
    tools=[
        WebScraper(off_prompt=True),
        TaskMemoryClient(off_prompt=True),
        FileManager()
    ]
)
agent.run("https://griptape.ai", "griptape.txt")
```

And here is the output:
```
[04/02/24 13:51:09] INFO     ToolkitTask 85700ec1b0594e1a9502c0efe7da6ef4
                             Input: Load https://griptape.ai, summarize it, and store it in a file called griptape.txt.
[04/02/24 13:51:15] INFO     Subtask db6a3e7cb2f549128c358149d340f91c
                             Thought: First, I need to load the content of the website using the WebScraper action. Then, I will use the TaskMemoryClient action to
                             summarize the content. Finally, I will save the summarized content to a file using the FileManager action.
                             Actions: [
                               {
                                 "name": "WebScraper",
                                 "path": "get_content",
                                 "input": {
                                   "values": {
                                     "url": "https://griptape.ai"
                                   }
                                 },
                                 "tag": "load_website_content"
                               }
                             ]
[04/02/24 13:51:16] INFO     Subtask db6a3e7cb2f549128c358149d340f91c
                             Response: Output of "WebScraper.get_content" was stored in memory with memory_name "TaskMemory" and artifact_namespace
                             "752b38bb86da4baabdbd9f444eb4a0d1"
[04/02/24 13:51:19] INFO     Subtask c3edba87ebf845d4b85e3a791f8fde8d
                             Thought: Now that the website content is loaded into memory, I need to summarize it using the TaskMemoryClient action.
                             Actions: [{"tag": "summarize_content", "name": "TaskMemoryClient", "path": "summarize", "input": {"values": {"memory_name": "TaskMemory",
                             "artifact_namespace": "752b38bb86da4baabdbd9f444eb4a0d1"}}}]
[04/02/24 13:51:25] INFO     Subtask c3edba87ebf845d4b85e3a791f8fde8d
                             Response: Output of "TaskMemoryClient.summarize" was stored in memory with memory_name "TaskMemory" and artifact_namespace
                             "c4f131c201f147dcab07be3925b46294"
[04/02/24 13:51:33] INFO     Subtask 06fe01ca64a744b38a8c08eb152aaacb
                             Thought: Now that the content has been summarized and stored in memory, I need to save this summarized content to a file named 'griptape.txt'
                             using the FileManager action.
                             Actions: [{"tag": "save_summarized_content", "name": "FileManager", "path": "save_memory_artifacts_to_disk", "input": {"values": {"dir_name":
                             ".", "file_name": "griptape.txt", "memory_name": "TaskMemory", "artifact_namespace": "c4f131c201f147dcab07be3925b46294"}}}]
                    INFO     Subtask 06fe01ca64a744b38a8c08eb152aaacb
                             Response: saved successfully
[04/02/24 13:51:35] INFO     ToolkitTask 85700ec1b0594e1a9502c0efe7da6ef4
                             Output: The summarized content of the website https://griptape.ai has been successfully saved to a file named 'griptape.txt'.
```

During the run, the Griptape Agent loaded a webpage with a [Tool](https://docs.griptape.ai/stable/griptape-tools/), stored its full content in [Task Memory](https://docs.griptape.ai/stable/griptape-framework/structures/task-memory.md), queried it to answer the original question, and finally saved the answer to a file.

The important thing to note here is that no matter how big the webpage is it can never blow up the prompt token limit because the full content of the page never goes back to the LLM. Additionally, no data from the subsequent subtasks were returned back to the prompt either. So, how does it work?

In the above example, we set [off_prompt](https://docs.griptape.ai/stable/griptape-framework/structures/task-memory.md#off-prompt) to `True`, which means that the LLM can never see the data it manipulates, but can send it to other Tools.

[Check out our docs](https://docs.griptape.ai/stable/griptape-framework/drivers/prompt-drivers/) to learn more about how to use Griptape with other LLM providers like Anthropic, Claude, Hugging Face, and Azure.

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

Run `make test/unit` to execute the test suite locally.

4. **Documentation:** Every pull request must include updates to documentation or explicitly explain why a documentation update is not required. Documentation is crucial for maintaining a comprehensive and user-friendly project.

Run `make docs` to build the documentation locally.

5. **Code Checks:** Griptape a variety of tools to enforce code quality and style. Your code must pass all checks before it can be merged.

Run `make check` to run all code checks locally.

6. **Changelog:** If your pull request introduces a notable change, please update the [changelog](https://github.com/griptape-ai/griptape/blob/dev/CHANGELOG.md).

### New Griptape Tools

Griptape's extensibility allows anyone to develop and distribute tools independently. With rare exceptions for Tools providing broadly applicable functionality, new Griptape Tools should be managed as their own projects and not submitted to the core framework. Pull requests for new tools (unless addressing an [existing issue](https://github.com/griptape-ai/griptape/issues)) will be closed.

The [Griptape Tool Template](https://github.com/griptape-ai/tool-template) provides the recommended structure, step-by-step instructions, basic automation, and usage examples for new Tools. In the Template, select **Use this template** then **Create a new repository** to begin a new Tool project.

### Dev and Test Dependencies

Install all dependencies via Make:

```shell
make install
```

Or install by calling Poetry directly:

```shell
poetry install --all-extras --with dev --with test --with docs
```

Configure pre-commit to ensure that your code is formatted correctly and passes all checks:

```shell
poetry run pre-commit install
```

## License

Griptape is available under the Apache 2.0 License.
