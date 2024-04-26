## Overview

Task Memory is a powerful feature of Griptape that allows you to control where the data returned by Tools is stored. This is useful in the following scenarios:


* **Security requirements**: many organizations don't want data to leave their cloud for regulatory and security reasons.
* **Long textual content**: when textual content returned by Tools can't fit in the token limit, it's often useful to perform operations on it in a separate process, not in the main LLM.
* **Non-textual content**: Tools can generate images, videos, PDFs, and other non-textual content that can be stored in Task Memory and acted upon later by other Tools.


## Off Prompt

You can enable or disable Task Memory on a Tool with the `off_prompt` parameter. When `off_prompt` is set to `True`, the Tool will store its output in Task Memory. When `off_prompt` is set to `False`, the Tool will return its output directly to the LLM.

By default, all Tools have `off_prompt` as a required parameter, forcing you to consider whether you'd like to use Task Memory or not. Lets look at a simple example where `off_prompt` is set to `False`:

```python
from griptape.structures import Agent
from griptape.tools import Calculator

# Create an agent with the Calculator tool
agent = Agent(
    tools=[Calculator(off_prompt=False)]
)

agent.run("What is 10 raised to the power of 5?")
```

```
[04/26/24 13:06:42] INFO     ToolkitTask 36b9dea13b9d479fb752014f41dca54c
                             Input: What is the square root of 12345?
[04/26/24 13:06:48] INFO     Subtask a88c0feeaef6493796a9148ed68c9caf
                             Thought: To find the square root of 12345, I can use the Calculator action with the expression "12345 ** 0.5".
                             Actions: [{"name": "Calculator", "path": "calculate", "input": {"values": {"expression": "12345 ** 0.5"}}, "tag": "sqrt_12345"}]
                    INFO     Subtask a88c0feeaef6493796a9148ed68c9caf
                             Response: 111.1080555135405
[04/26/24 13:06:49] INFO     ToolkitTask 36b9dea13b9d479fb752014f41dca54c
                             Output: The square root of 12345 is approximately 111.108.
```

Since the result of the Calculator Tool is neither sensitive nor too large, we can set `off_prompt` to `False` and not use Task Memory.

Let's explore what happens when `off_prompt` is set to `True`:

```python
from griptape.structures import Agent
from griptape.tools import Calculator

# Create an agent with the Calculator tool
agent = Agent(
    tools=[Calculator(off_prompt=True)]
)

agent.run("What is 10 raised to the power of 5?")
```


```
[04/26/24 13:07:02] INFO     ToolkitTask ecbb788d9830491ab72a8a2bbef5fb0a
                             Input: What is the square root of 12345?
[04/26/24 13:07:10] INFO     Subtask 4700dc0c2e934d1a9af60a28bd770bc6
                             Thought: To find the square root of a number, we can use the Calculator action with the expression "sqrt(12345)". However, the Calculator
                             action only supports basic arithmetic operations and does not support the sqrt function. Therefore, we need to use the equivalent expression
                             for square root which is raising the number to the power of 0.5.
                             Actions: [{"name": "Calculator", "path": "calculate", "input": {"values": {"expression": "12345**0.5"}}, "tag": "sqrt_calculation"}]
                    INFO     Subtask 4700dc0c2e934d1a9af60a28bd770bc6
                             Response: Output of "Calculator.calculate" was stored in memory with memory_name "TaskMemory" and artifact_namespace
                             "6be74c5128024c0588eb9bee1fdb9aa5"
[04/26/24 13:07:16] ERROR    Subtask ecbb788d9830491ab72a8a2bbef5fb0a
                             Invalid action JSON: Or({Literal("name", description=""): 'Calculator', Literal("path", description="Can be used for computing simple
                             numerical or algebraic calculations in Python"): 'calculate', Literal("input", description=""): {'values': Schema({Literal("expression",
                             description="Arithmetic expression parsable in pure Python. Single line only. Don't use variables. Don't use any imports or external
                             libraries"): <class 'str'>})}, Literal("tag", description="Unique tag name for action execution."): <class 'str'>}) did not validate {'name':
                             'Memory', 'path': 'get', 'input': {'memory_name': 'TaskMemory', 'artifact_namespace': '6be74c5128024c0588eb9bee1fdb9aa5'}, 'tag':
                             'get_sqrt_result'}
                             Key 'name' error:
                             'Calculator' does not match 'Memory'
...Output truncated for brevity...
```

When we set `off_prompt` to `True`, the Agent does not function as expected, even generating an error. This is because because the Calculator output is being stored in Task Memory but the Agent has no way to access it. To fix this, we need the `TaskMemoryClient`.

## Task Memory Client

The [TaskMemoryClient](../griptape-tools/official-tools/task-memory-client.md) is a Tool that allows an Agent to interact with Task Memory. It has the following methods:

- `query`: Retrieve the content of an Artifact stored in Task Memory.
- `summarize`: Summarize the content of an Artifact stored in Task Memory.

Let's add `TaskMemoryClient` to the Agent and run the same task:

```python
from griptape.structures import Agent
from griptape.tools import Calculator, TaskMemoryClient

# Create an agent with the Calculator tool
agent = Agent(tools=[Calculator(off_prompt=True), TaskMemoryClient(off_prompt=False)])

agent.run("What is the square root of 12345?")
```

```
[04/26/24 13:13:01] INFO     ToolkitTask 5b46f9ef677c4b31906b48aba3f45e2c
                             Input: What is the square root of 12345?
[04/26/24 13:13:07] INFO     Subtask 611d98ea5576430fbc63259420577ab2
                             Thought: To find the square root of 12345, I can use the Calculator action with the expression "12345 ** 0.5".
                             Actions: [{"name": "Calculator", "path": "calculate", "input": {"values": {"expression": "12345 ** 0.5"}}, "tag": "sqrt_12345"}]
[04/26/24 13:13:08] INFO     Subtask 611d98ea5576430fbc63259420577ab2
                             Response: Output of "Calculator.calculate" was stored in memory with memory_name "TaskMemory" and artifact_namespace
                             "7554b69e1d414a469b8882e2266dcea1"
[04/26/24 13:13:15] INFO     Subtask 32b9163a15644212be60b8fba07bd23b
                             Thought: The square root of 12345 has been calculated and stored in memory. I can retrieve this value using the TaskMemoryClient action with
                             the query path, providing the memory_name and artifact_namespace as input.
                             Actions: [{"tag": "retrieve_sqrt", "name": "TaskMemoryClient", "path": "query", "input": {"values": {"memory_name": "TaskMemory",
                             "artifact_namespace": "7554b69e1d414a469b8882e2266dcea1", "query": "What is the result of the calculation?"}}}]
[04/26/24 13:13:16] INFO     Subtask 32b9163a15644212be60b8fba07bd23b
                             Response: The result of the calculation is 111.1080555135405.
[04/26/24 13:13:17] INFO     ToolkitTask 5b46f9ef677c4b31906b48aba3f45e2c
                             Output: The square root of 12345 is approximately 111.108.
```

Note that on the `TaskMemoryClient` we've set `off_prompt` to `False` so that the results of the query can be returned directly to the LLM. If we had kept it as `True`, the results would have been stored back Task Memory which would've put us back to square one.

While this fixed the problem, it took a handful more steps than when we just had `Calculator(off_prompt=False)`. Let's look at a more complex example where Task Memory shines.

## Large Data

Let's say we want to query the contents of a very large webpage.

```python
from griptape.structures import Agent
from griptape.tools import WebScraper

# Create an agent with the Calculator tool
agent = Agent(tools=[WebScraper(off_prompt=False)])

agent.run(
    "According to this page https://en.wikipedia.org/wiki/Elden_Ring, how many copies of Elden Ring have been sold?"
)
```

When running this example, we get the following error:
```
[04/26/24 13:20:02] ERROR    ToolkitTask 67e2f907f95d4850ae79f9da67df54c1
                             Error code: 400 - {'error': {'message': "This model's maximum context length is 8192 tokens. However, your messages resulted in 73874 tokens.
                             Please reduce the length of the messages.", 'type': 'invalid_request_error', 'param': 'messages', 'code': 'context_length_exceeded'}}
```

This is because the content of the webpage is too large to fit in the LLM's input token limit. We can fix this by storing the content in Task Memory, and then querying it with the `TaskMemoryClient`.

```python
from griptape.structures import Agent
from griptape.tools import WebScraper, TaskMemoryClient

agent = Agent(
    tools=[
        WebScraper(off_prompt=True),
        TaskMemoryClient(off_prompt=False),
    ]
)

agent.run(
    "According to this page https://en.wikipedia.org/wiki/Elden_Ring, how many copies of Elden Ring have been sold?"
)
```

And now we get the expected output:
```
[04/26/24 13:51:51] INFO     ToolkitTask 7aca20f202df47a2b9848ed7025f9c21
                             Input: According to this page https://en.wikipedia.org/wiki/Elden_Ring, how many copies of Elden Ring have been sold?
[04/26/24 13:51:58] INFO     Subtask 5b21d8ead32b4644abcd1e852bb5f512
                             Thought: I need to scrape the content of the provided URL to find the information about how many copies of Elden Ring have been sold.
                             Actions: [{"name": "WebScraper", "path": "get_content", "input": {"values": {"url": "https://en.wikipedia.org/wiki/Elden_Ring"}}, "tag":
                             "scrape_elden_ring"}]
[04/26/24 13:52:04] INFO     Subtask 5b21d8ead32b4644abcd1e852bb5f512
                             Response: Output of "WebScraper.get_content" was stored in memory with memory_name "TaskMemory" and artifact_namespace
                             "2d4ebc7211074bb7be26613eb25d8fc1"
[04/26/24 13:52:11] INFO     Subtask f12eb3d3b4924e4085808236b460b43d
                             Thought: Now that the webpage content is stored in memory, I need to query this memory to find the information about how many copies of Elden
                             Ring have been sold.
                             Actions: [{"tag": "query_sales", "name": "TaskMemoryClient", "path": "query", "input": {"values": {"memory_name": "TaskMemory",
                             "artifact_namespace": "2d4ebc7211074bb7be26613eb25d8fc1", "query": "How many copies of Elden Ring have been sold?"}}}]
[04/26/24 13:52:14] INFO     Subtask f12eb3d3b4924e4085808236b460b43d
                             Response: Elden Ring sold 23 million copies by February 2024.
[04/26/24 13:52:15] INFO     ToolkitTask 7aca20f202df47a2b9848ed7025f9c21
                             Output: Elden Ring sold 23 million copies by February 2024.
```

## Sensitive Data

Because Task Memory splits up the storage and retrieval of data, you can use different models for each step.

Here is an example where we use GPT-4 to orchestrate the Tools and store the data in Task Memory, and a self-hosted Llama-2 model to summarize the raw content.

```python 
import os

from griptape.config import (
    OpenAiStructureConfig,
    StructureGlobalDriversConfig,
    StructureTaskMemoryConfig,
    StructureTaskMemorySummaryEngineConfig,
    StructureTaskMemoryQueryEngineConfig,
)
from griptape.drivers import (
    HuggingFaceHubPromptDriver,
    LocalVectorStoreDriver,
    OpenAiChatPromptDriver,
    HuggingFaceHubEmbeddingDriver,
)
from griptape.structures import Agent
from griptape.tokenizers import HuggingFaceTokenizer
from griptape.tools import TaskMemoryClient, WebScraper, FileManager
from transformers import LlamaTokenizerFast, AutoTokenizer

agent = Agent(
    config=OpenAiStructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=OpenAiChatPromptDriver(model="gpt-4"),
        ),
        task_memory=StructureTaskMemoryConfig(
            query_engine=StructureTaskMemoryQueryEngineConfig(
                prompt_driver=HuggingFaceHubPromptDriver(
                    api_token=os.environ["HUGGINGFACE_HUB_ACCESS_TOKEN"],
                    model="meta-llama/Llama-2-7b-chat-hf",
                    tokenizer=HuggingFaceTokenizer(
                        tokenizer=LlamaTokenizerFast.from_pretrained(
                            "meta-llama/Llama-2-7b-chat-hf"
                        ),
                        max_input_tokens=4096,
                        max_output_tokens=1024,
                    ),
                ),
                vector_store_driver=LocalVectorStoreDriver(
                    embedding_driver=HuggingFaceHubEmbeddingDriver(
                        api_token=os.environ["HUGGINGFACE_HUB_ACCESS_TOKEN"],
                        model="sentence-transformers/all-MiniLM-L6-v2",
                        tokenizer=HuggingFaceTokenizer(
                            max_output_tokens=512,
                            tokenizer=AutoTokenizer.from_pretrained(
                                "sentence-transformers/all-MiniLM-L6-v2"
                            ),
                        ),
                    )
                ),
            ),
            summary_engine=StructureTaskMemorySummaryEngineConfig(
                prompt_driver=HuggingFaceHubPromptDriver(
                    api_token=os.environ["HUGGINGFACE_HUB_ACCESS_TOKEN"],
                    model="meta-llama/Llama-2-7b-chat-hf",
                    tokenizer=HuggingFaceTokenizer(
                        tokenizer=LlamaTokenizerFast.from_pretrained(
                            "meta-llama/Llama-2-7b-chat-hf"
                        ),
                        max_input_tokens=4096,
                        max_output_tokens=1024,
                    ),
                ),
            ),
        ),
    ),
    tools=[
        WebScraper(off_prompt=True),
        TaskMemoryClient(off_prompt=True, allowlist=["summarize"]),
        FileManager(off_prompt=True),
    ],
)

agent.run(
    "Generate a summary of this webpage: https://simple.wikipedia.org/wiki/San_Francisco and then save it to a file."
)


```

```
[04/26/24 14:44:35] INFO     ToolkitTask 1ed8480fa2dc42d7ac56165491869efc
                             Input: Generate a summary of this webpage: https://simple.wikipedia.org/wiki/San_Francisco and then save it to a file.
[04/26/24 14:44:41] INFO     Subtask 51f637e66a7d415488b4912834475bee
                             Thought: First, I need to scrape the content of the webpage. Then, I will summarize the content and finally save the summary to a file.
                             Actions: [{"name": "WebScraper", "path": "get_content", "input": {"values": {"url": "https://simple.wikipedia.org/wiki/San_Francisco"}},
                             "tag": "scrape_webpage"}]
[04/26/24 14:44:46] INFO     Subtask 51f637e66a7d415488b4912834475bee
                             Response: Output of "WebScraper.get_content" was stored in memory with memory_name "TaskMemory" and artifact_namespace
                             "9a43acd36a24440cb436c0fef189c534"
[04/26/24 14:44:51] INFO     Subtask 269c537132b3461386c5032cea719805
                             Thought: Now that the webpage content is stored in memory, I need to summarize it.
                             Actions: [{"tag": "summarize_content", "name": "TaskMemoryClient", "path": "summarize", "input": {"values": {"memory_name": "TaskMemory",
                             "artifact_namespace": "9a43acd36a24440cb436c0fef189c534"}}}]
[04/26/24 14:45:57] INFO     Subtask 269c537132b3461386c5032cea719805
                             Response: Output of "TaskMemoryClient.summarize" was stored in memory with memory_name "TaskMemory" and artifact_namespace
                             "fe04d7543ac64aecab6b00f5417f5bfb"
[04/26/24 14:46:02] INFO     Subtask 2618fc23194947018ce7d3facb33e5b9
                             Thought: Now that the summary is stored in memory, I need to save it to a file.
                             Actions: [{"tag": "save_summary", "name": "FileManager", "path": "save_memory_artifacts_to_disk", "input": {"values": {"dir_name":
                             "summaries", "file_name": "san_francisco_summary.txt", "memory_name": "TaskMemory", "artifact_namespace":
                             "fe04d7543ac64aecab6b00f5417f5bfb"}}}]
                    INFO     Subtask 2618fc23194947018ce7d3facb33e5b9
                             Response: Successfully saved memory artifacts to disk
[04/26/24 14:46:04] INFO     ToolkitTask 1ed8480fa2dc42d7ac56165491869efc
                             Output: The summary of the webpage has been successfully saved to the file "san_francisco_summary.txt" in the "summaries" directory.

```

Note that in this example GPT-4 _never_ saw the contents of the page, only that it was stored in Task Memory.

!!! info
    In this instance of using `FileManager` to save a file to disk, it does not matter what the value of `off_prompt` is set to. This Tool Activity returns an `InfoArtifact` which Griptape will not store in Task Memory. Griptape will only store `TextArtifact`'s, `BlobArtifact`'s, and `ListArtifact`'s in Task Memory.

## Tools That Use Task Memory

As seen in the previous example, certain Tools are designed to read directly from Task Memory. This means that you can use these Tools to interact with the data stored in Task Memory without needing to pass it through the LLM.

Today, these include:

- [TaskMemoryClient](../griptape-tools/official-tools/task-memory-client.md)
- [FileManager](../griptape-tools/official-tools/file-manager.md)
- [AwsS3Client](../griptape-tools/official-tools/aws-s3-client.md)
- [GoogleDriveClient](../griptape-tools/official-tools/google-drive-client.md)
- [GoogleDocsClient](../griptape-tools/official-tools/google-docs-client.md)
