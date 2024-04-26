## Overview

Task Memory is a powerful feature of Griptape that allows you to control where the data returned by Tools is stored. This is useful in the following scenarios:


* **Security requirements**: many organizations don't want data to leave their cloud for regulatory and security reasons.
* **Long textual content**: when textual content returned by Tools can't fit in the token limit, it's often useful to perform operations on it in a separate process, not in the main LLM.
* **Non-textual content**: Rools can generate images, videos, PDFs, and other non-textual content that can be stored in Task Memory and acted upon later by other Tools.


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

And the output:
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


The output will be:
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

When we set `off_prompt` to `True`, the Agent does not function as expected, evening generating an error. This is because because the Calculator output is being stored in Task Memory but the Agent has no way to access it. To fix this, we need the `TaskMemoryClient`.

## Task Memory Client

The [TaskMemoryClient](../griptape-tools/official-tools/task-memory-client.md) is a tool that allows an Agent to interact with Task Memory. It has the following methods:

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

And the successful output:
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

While this fixed the problem, it took a handful more steps than when we just had `Calculator(off_prompt=False)`. A simple example like this is an example where Task Memory is _not_ the best solution; it simply adds complexity without much benefit.

However, let's look at a more complex example where Task Memory shines.


## Large Data

Let's say we want to query the contents of a very large webpage.

```python
from griptape.structures import Agent
from griptape.tools import WebScraper

# Create an agent with the Calculator tool
agent = Agent(tools=[WebScraper(off_prompt=False)])

agent.run(
    "According to this page https://en.wikipedia.org/wiki/List_of_cities_by_average_precipitation, what is the average precipitation in the city of San Francisco?"
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

# Create an agent with the Calculator tool
agent = Agent(tools=[WebScraper(off_prompt=True), TaskMemoryClient(off_prompt=True)])

agent.run(
    "According to this page https://en.wikipedia.org/wiki/List_of_cities_by_average_precipitation, what is the average precipitation in the city of San Francisco?"
)
```

## Task Memory
Here is an example of how memory can be used in unison with multiple tools to store and load content:

```python
from griptape.artifacts import TextArtifact, BlobArtifact
from griptape.memory.task.storage import TextArtifactStorage, BlobArtifactStorage
from griptape.structures import Agent
from griptape.tools import WebScraper, FileManager, TaskMemoryClient
from griptape.engines import VectorQueryEngine, PromptSummaryEngine, CsvExtractionEngine, JsonExtractionEngine
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver, OpenAiChatPromptDriver

prompt_driver = OpenAiChatPromptDriver(model="gpt-3.5-turbo")

agent = Agent(
    tools=[WebScraper(off_prompt=True), FileManager(off_prompt=True), TaskMemoryClient(off_prompt=True)]
)

agent.run(
    "Load https://www.griptape.ai, summarize it, "
    "and store it in griptape.txt"
)
```

```
[10/20/23 13:31:40] INFO     ToolkitTask 82211eeb10374e75ad77135373d816e6       
                             Input: Load https://www.griptape.ai, summarize it, 
                             and store it in griptape.txt                       
[10/20/23 13:31:52] INFO     Subtask 17b3d35197eb417b834a7db49039ae4f           
                             Thought: The user wants to load the webpage at     
                             https://www.griptape.ai, summarize its content, and
                             store the summary in a file named griptape.txt. To 
                             achieve this, I need to first use the WebScraper   
                             tool to get the content of the webpage. Then, I    
                             will use the TaskMemoryClient to summarize the  
                             content. Finally, I will use the FileManager tool  
                             to save the summarized content to a file named     
                             griptape.txt.                                      
                                                                                
                             Action: {"name": "WebScraper",     
                             "path": "get_content", "input": {"values":     
                             {"url": "https://www.griptape.ai"}}}               
[10/20/23 13:31:53] INFO     Subtask 17b3d35197eb417b834a7db49039ae4f           
                             Response: Output of "WebScraper.get_content" was
                             stored in memory with memory_name "TaskMemory" and 
                             artifact_namespace                                 
                             "82543abe79984d11bb952bd6036a7a01"                 
[10/20/23 13:32:00] INFO     Subtask 58bac35adda94157ac6f9482e7c41c9f           
                             Thought: Now that I have the content of the webpage
                             stored in memory, I can use the TaskMemoryClient
                             tool to summarize this content.                    
                             Action: {"name":                   
                             "TaskMemoryClient", "path": "summarize",    
                             "input": {"values": {"memory_name": "TaskMemory",  
                             "artifact_namespace":                              
                             "82543abe79984d11bb952bd6036a7a01"}}}              
[10/20/23 13:32:03] INFO     Subtask 58bac35adda94157ac6f9482e7c41c9f           
                             Response: Output of                             
                             "TaskMemoryClient.summarize" was stored in      
                             memory with memory_name "TaskMemory" and           
                             artifact_namespace                                 
                             "01b8015f8c5647f09e8d103198404db0"                 
[10/20/23 13:32:12] INFO     Subtask a630f649007b4d7fa0b6cf85be6b2f4f           
                             Thought: Now that I have the summarized content of 
                             the webpage stored in memory, I can use the        
                             FileManager tool to save this content to a file    
                             named griptape.txt.                                
                             Action: {"name": "FileManager",    
                             "path": "save_memory_artifacts_to_disk",       
                             "input": {"values": {"dir_name": ".", "file_name": 
                             "griptape.txt", "memory_name": "TaskMemory",       
                             "artifact_namespace":                              
                             "01b8015f8c5647f09e8d103198404db0"}}}              
                    INFO     Subtask a630f649007b4d7fa0b6cf85be6b2f4f           
                             Response: saved successfully                    
[10/20/23 13:32:14] INFO     ToolkitTask 82211eeb10374e75ad77135373d816e6       
                             Output: The summarized content of the webpage at   
                             https://www.griptape.ai has been successfully      
                             stored in a file named griptape.txt. 
```
