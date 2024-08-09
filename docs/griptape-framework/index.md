The Griptape framework provides developers with the ability to create AI systems that operate across two dimensions: **predictability** and **creativity**. 

For **predictability**, Griptape enforces structures like sequential pipelines, DAG-based workflows, and long-term memory. To facilitate creativity, Griptape safely prompts LLMs with tools and short-term memory connecting them to external APIs and data stores. The framework allows developers to transition between those two dimensions effortlessly based on their use case.

Griptape not only helps developers harness the potential of LLMs but also enforces trust boundaries, schema validation, and tool activity-level permissions. By doing so, Griptape maximizes LLMs’ reasoning while adhering to strict policies regarding their capabilities.

Griptape’s design philosophy is based on the following tenets:

1. **Modularity and composability**: All framework primitives are useful and usable on their own in addition to being easy to plug into each other.
2. **Technology-agnostic**: Griptape is designed to work with any capable LLM, data store, and backend through the abstraction of drivers.
3. **Keep data off prompt by default**: When working with data through loaders and tools, Griptape aims to keep it off prompt by default, making it easy to work with big data securely and with low latency.
4. **Minimal prompt engineering**: It’s much easier to reason about code written in Python, not natural languages. Griptape aims to default to Python in most cases unless absolutely necessary.

## Quick Start

### OpenAI API Key
First, configure an OpenAI client by [getting an API key](https://platform.openai.com/account/api-keys) and adding it to your environment as `OPENAI_API_KEY`. 
By default, Griptape uses [OpenAI Completions API](https://platform.openai.com/docs/guides/completion) to execute LLM prompts, but other LLMs can be configured with the use of [Prompt Drivers](./drivers/prompt-drivers.md).

### Using pip

Install **griptape**:

```
pip install "griptape[all]" -U
```

### Using Poetry

To get started with Griptape using Poetry first create a new poetry project from the terminal: 

```
poetry new griptape-quickstart
```

Change your working directory to the new `griptape-quickstart` directory created by Poetry and add the the `griptape` dependency. 

```
poetry add "griptape[all]"
```

### Extras

The `[all]` [extra](https://peps.python.org/pep-0508/#extras) ensures that you have access to the entire range of functionalities that Griptape offers. 
This comprehensive installation is recommended for newcomers to get the complete Griptape experience.

However, if you wish to optimize the installation size or only require specific functionalities, you have two main options:

1. Core Dependencies: These are the foundational dependencies that enable Griptape to function with most of its default settings.
2. Extras: These are additional, vendor-specific drivers integrated within the Griptape framework. If a particular Driver mandates an extra, it will be explicitly highlighted in the documentation.

To install just the core dependencies:
```
poetry add griptape
```

To install specific extras (e.g., drivers for [AnthropicPromptDriver](./drivers/prompt-drivers.md#anthropic) and [PineconeVectorStoreDriver](./drivers/vector-store-drivers.md#pinecone)):
```
poetry add "griptape[drivers-prompt-anthropic,drivers-vector-pinecone]"
```

For a comprehensive list of extras, please refer to the `[tool.poetry.extras]` section of Griptape's [pyproject.toml](https://github.com/griptape-ai/griptape/blob/main/pyproject.toml).

## Build a Simple Agent 
With Griptape, you can create *structures*, such as [Agents](./structures/agents.md), [Pipelines](./structures/pipelines.md), and [Workflows](./structures/workflows.md), that are composed of different types of tasks. First, let's build a simple Agent that we can interact with through a chat based interface. 

```python
--8<-- "docs/griptape-framework/src/index_1.py"
```
Run this script in your IDE and you'll be presented with a `Q:` prompt where you can interact with your model. 
```
Q: Write me a haiku about griptape
processing...
[09/08/23 09:52:45] INFO     PromptTask d4302227570e4a978ed79e7e0444337b
                             Input: Write me a haiku about griptape
[09/08/23 09:52:48] INFO     PromptTask d4302227570e4a978ed79e7e0444337b
                             Output: Griptape rough and true,
                             Skateboard's trusty, silent guide,
                             In each ride, we're glued.
A: Griptape rough and true,
Skateboard's trusty, silent guide,
In each ride, we're glued.
Q:
```
If you want to skip the chat interface and load an initial prompt, you can do so using the `.run()` method: 

```python
--8<-- "docs/griptape-framework/src/index_2.py"
```
Agents on their own are fun, but let's add some capabilities to them using Griptape Tools. 
### Build a Simple Agent with Tools 

```python
--8<-- "docs/griptape-framework/src/index_3.py"
```
Here is the chain of thought from the Agent. Notice where it realizes it can use the tool you just injected to do the calculation.[^1] 
[^1]: In some cases a model might be capable of basic arithmetic. For example, gpt-3.5 returns the correct numeric answer but in an odd format.

```
[07/23/24 10:47:38] INFO     ToolkitTask 6a51060d1fb74e57840a91aa319f26dc
                             Input: what is 7^12
[07/23/24 10:47:39] INFO     Subtask 0c984616fd2345a7b48a0b0d692daa3c
                             Actions: [
                               {
                                 "tag": "call_RTRm7JLFV0F73dCVPmoWVJqO",
                                 "name": "Calculator",
                                 "path": "calculate",
                                 "input": {
                                   "values": {
                                     "expression": "7**12"
                                   }
                                 }
                               }
                             ]
                    INFO     Subtask 0c984616fd2345a7b48a0b0d692daa3c
                             Response: 13841287201
[07/23/24 10:47:40] INFO     ToolkitTask 6a51060d1fb74e57840a91aa319f26dc
                             Output: 13,841,287,201
Answer: 13,841,287,201
```

## Build a Simple Pipeline

Agents are great for getting started, but they are intentionally limited to a single task. Pipelines, however, allow us to define any number of tasks to run in sequence. Let's define a simple two-task Pipeline that uses tools and memory:

```python
--8<-- "docs/griptape-framework/src/index_4.py"
```

```
[09/08/23 10:02:34] INFO     ToolkitTask 3c1d2f4a49384873820a9a8cd8acc983
                             Input: Load https://www.griptape.ai, summarize it, and store it in griptape.txt
[09/08/23 10:02:44] INFO     Subtask 42fd56ba100e45688401c5ce32b79a33
                             Thought: To complete this task, I need to first load the webpage using the WebScraper tool's get_content
                             activity. Then, I will summarize the content using the TaskMemory tool's summarize activity. Finally, I will
                             store the summarized content in a file named griptape.txt using the FileManager tool's save_file_to_disk
                             activity.

                             Action: {"name": "WebScraper", "path": "get_content", "input": {"values": {"url":
                             "https://www.griptape.ai"}}}
[09/08/23 10:02:45] INFO     Subtask 42fd56ba100e45688401c5ce32b79a33
                             Response: Output of "WebScraper.get_content" was stored in memory with memory_name "TaskMemory" and
                             artifact_namespace "39ca67bbe26b4e1584193b87ed82170d"
[09/08/23 10:02:53] INFO     Subtask 8023e3d257274df29065b22e736faca8
                             Thought: Now that the webpage content is stored in memory, I can use the TaskMemory tool's summarize activity
                             to summarize the content.
                             Action: {"name": "TaskMemoryClient", "path": "summarize", "input": {"values": {"memory_name": "TaskMemory", "artifact_namespace": "39ca67bbe26b4e1584193b87ed82170d"}}}
[09/08/23 10:02:57] INFO     Subtask 8023e3d257274df29065b22e736faca8
                             Response: Griptape is an open source framework that allows developers to build and deploy AI applications
                             using large language models (LLMs). It provides the ability to create conversational and event-driven apps that
                             can securely access and manipulate data. The framework enforces structures for predictability and creativity,
                             allowing developers to easily transition between the two. Griptape Cloud is a managed platform for deploying and
                             managing AI apps.
[09/08/23 10:03:06] INFO     Subtask 7baae700239943c18b5b6b21873f0e13
                             Thought: Now that I have the summarized content, I can store it in a file named griptape.txt using the
                             FileManager tool's save_file_to_disk activity.
                             Action: {"name": "FileManager", "path": "save_file_to_disk", "input": {"values":
                             {"memory_name": "TaskMemory", "artifact_namespace": "39ca67bbe26b4e1584193b87ed82170d", "path":
                             "griptape.txt"}}}
                    INFO     Subtask 7baae700239943c18b5b6b21873f0e13
                             Response: saved successfully
[09/08/23 10:03:14] INFO     ToolkitTask 3c1d2f4a49384873820a9a8cd8acc983
                             Output: The summarized content of the webpage https://www.griptape.ai has been successfully stored in the file
                             named griptape.txt.
                    INFO     PromptTask 8635925ff23b46f28a740105bd11ca8f
                             Input: Say the following in spanish: The summarized content of the webpage https://www.griptape.ai has been
                             successfully stored in the file named griptape.txt.
[09/08/23 10:03:18] INFO     PromptTask 8635925ff23b46f28a740105bd11ca8f
                             Output: El contenido resumido de la página web https://www.griptape.ai se ha almacenado con éxito en el archivo
                             llamado griptape.txt.
```
