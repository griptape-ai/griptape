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

- 🗣️ **Prompt Drivers** manage textual and image interactions with LLMs.
- 🔢 **Embedding Drivers** generate vector embeddings from textual inputs.
- 💾 **Vector Store Drivers** manage the storage and retrieval of embeddings.
- 🎨 **Image Generation Drivers** create images from text descriptions.
- 💼 **SQL Drivers** interact with SQL databases.
- 🌐 **Web Scraper Drivers** extract information from web pages.
- 🧠 **Conversation Memory Drivers** manage the storage and retrieval of conversational data.
- 📡 **Event Listener Drivers** forward framework events to external services.
- 🏗️ **Structure Run Drivers** execute structures both locally and in the cloud.
- 🤖 **Assistant Drivers** enable interactions with various "assistant" services.
- 🗣️ **Text to Speech Drivers** convert text to speech.
- 🎙️ **Audio Transcription Drivers** convert audio to text.
- 🔍 **Web Search Drivers** search the web for information.
- 📈 **Observability Drivers** send trace and event data to observability platforms.
- 📜 **Ruleset Drivers** load and apply rulesets from external sources.
- 🗂️ **File Manager Drivers** handle file operations on local and remote storage.

### 🚂 Engines

Engines wrap Drivers and provide use-case-specific functionality:

- 📊 **RAG Engine** is an abstraction for implementing modular Retrieval Augmented Generation (RAG) pipelines.
- 🛠️ **Extraction Engine** extracts JSON or CSV data from unstructured text.
- 📝 **Summary Engine** generates summaries from textual content.
- ✅ **Eval Engine** evaluates and scores the quality of generated text.

### 📦 Additional Components

- 📐 **Rulesets** steer LLM behavior with minimal prompt engineering.
- 🔄 **Loaders** load data from various sources.
- 🏺 **Artifacts** allow for passing data of different types between Griptape components.
- ✂️ **Chunkers** segment texts into manageable pieces for diverse text types.
- 🔢 **Tokenizers** count the number of tokens in a text to not exceed LLM token limits.

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
from griptape.tools import WebScraperTool, FileManagerTool, PromptSummaryTool

agent = Agent(
    input="Load {{ args[0] }}, summarize it, and store it in a file called {{ args[1] }}.",
    tools=[
        WebScraperTool(off_prompt=True),
        PromptSummaryTool(off_prompt=True),
        FileManagerTool()
    ]
)
agent.run("https://griptape.ai", "griptape.txt")
```

And here is the output:

```
[08/12/24 14:48:15] INFO     PromptTask c90d263ec69046e8b30323c131ae4ba0
                             Input: Load https://griptape.ai, summarize it, and store it in a file called griptape.txt.
[08/12/24 14:48:16] INFO     Subtask ebe23832cbe2464fb9ecde9fcee7c30f
                             Actions: [
                               {
                                 "tag": "call_62kBnkswnk9Y6GH6kn1GIKk6",
                                 "name": "WebScraperTool",
                                 "path": "get_content",
                                 "input": {
                                   "values": {
                                     "url": "https://griptape.ai"
                                   }
                                 }
                               }
                             ]
[08/12/24 14:48:17] INFO     Subtask ebe23832cbe2464fb9ecde9fcee7c30f
                             Response: Output of "WebScraperTool.get_content" was stored in memory with memory_name "TaskMemory" and artifact_namespace
                             "cecca28eb0c74bcd8c7119ed7f790c95"
[08/12/24 14:48:18] INFO     Subtask dca04901436d49d2ade86cd6b4e1038a
                             Actions: [
                               {
                                 "tag": "call_o9F1taIxHty0mDlWLcAjTAAu",
                                 "name": "PromptSummaryTool",
                                 "path": "summarize",
                                 "input": {
                                   "values": {
                                     "summary": {
                                       "memory_name": "TaskMemory",
                                       "artifact_namespace": "cecca28eb0c74bcd8c7119ed7f790c95"
                                     }
                                   }
                                 }
                               }
                             ]
[08/12/24 14:48:21] INFO     Subtask dca04901436d49d2ade86cd6b4e1038a
                             Response: Output of "PromptSummaryTool.summarize" was stored in memory with memory_name "TaskMemory" and artifact_namespace
                             "73765e32b8404e32927822250dc2ae8b"
[08/12/24 14:48:22] INFO     Subtask c233853450fb4fd6a3e9c04c52b33bf6
                             Actions: [
                               {
                                 "tag": "call_eKvIUIw45aRYKDBpT1gGKc9b",
                                 "name": "FileManagerTool",
                                 "path": "save_memory_artifacts_to_disk",
                                 "input": {
                                   "values": {
                                     "dir_name": ".",
                                     "file_name": "griptape.txt",
                                     "memory_name": "TaskMemory",
                                     "artifact_namespace": "73765e32b8404e32927822250dc2ae8b"
                                   }
                                 }
                               }
                             ]
                    INFO     Subtask c233853450fb4fd6a3e9c04c52b33bf6
                             Response: Successfully saved memory artifacts to disk
[08/12/24 14:48:23] INFO     PromptTask c90d263ec69046e8b30323c131ae4ba0
                             Output: The content from https://griptape.ai has been summarized and stored in a file called `griptape.txt`.
```

During the run, the Griptape Agent loaded a webpage with a [Tool](https://docs.griptape.ai/stable/griptape-tools/), stored its full content in [Task Memory](https://docs.griptape.ai/stable/griptape-framework/structures/task-memory.md), queried it to answer the original question, and finally saved the answer to a file.

The important thing to note here is that no matter how big the webpage is it can never blow up the prompt token limit because the full content of the page never goes back to the LLM. Additionally, no data from the subsequent subtasks were returned back to the prompt either. So, how does it work?

In the above example, we set [off_prompt](https://docs.griptape.ai/stable/griptape-framework/structures/task-memory.md#off-prompt) to `True`, which means that the LLM can never see the data it manipulates, but can send it to other Tools.

> [!IMPORTANT]
> This example uses Griptape's [PromptTask](https://docs.griptape.ai/stable/griptape-framework/structures/tasks/#prompt-task) with `tools`, which requires a highly capable LLM to function correctly. By default, Griptape uses the [OpenAiChatPromptDriver](https://docs.griptape.ai/stable/griptape-framework/drivers/prompt-drivers/#openai-chat); for another powerful LLM try swapping to the [AnthropicPromptDriver](https://docs.griptape.ai/stable/griptape-framework/drivers/prompt-drivers/#anthropic)!
> If you're using a less powerful LLM, consider using the [ToolTask](https://docs.griptape.ai/stable/griptape-framework/structures/tasks/#tool-task) instead, as the `PromptTask` with `tools` might not work properly or at all.

[Check out our docs](https://docs.griptape.ai/stable/griptape-framework/drivers/prompt-drivers/) to learn more about how to use Griptape with other LLM providers like Anthropic, Claude, Hugging Face, and Azure.

## Versioning

Griptape uses [Semantic Versioning](https://semver.org/).

## Contributing

Thank you for considering contributing to Griptape! Before you start, please review our [Contributing Guidelines](https://github.com/griptape-ai/griptape/blob/main/CONTRIBUTING.md).

## License

Griptape is available under the Apache 2.0 License.
