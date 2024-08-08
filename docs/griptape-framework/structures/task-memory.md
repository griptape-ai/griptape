---
search:
  boost: 2 
---

## Overview

Task Memory is a powerful feature of Griptape that allows you to control where the data returned by [Tools](../tools/index.md) is stored. This is useful in the following scenarios:

* **Security requirements**: many organizations don't want data to leave their cloud for regulatory and security reasons.
* **Long textual content**: when textual content returned by Tools can't fit in the token limit, it's often useful to perform actions on it as a separate operation, not through the main LLM.
* **Non-textual content**: Tools can generate images, videos, PDFs, and other non-textual content that can be stored in Task Memory and acted upon later by other Tools.

!!! tip
    Running into issue with Task Memory? Check out the [Task Memory Considerations](#task-memory-considerations) section for some common pitfalls.

## Off Prompt

You can enable or disable sending a Tool's results to Task Memory with the `off_prompt` parameter. By default, all Tools have `off_prompt` set to `False` making this an opt-in feature.
When `off_prompt` is set to `True`, the Tool will store its output in Task Memory. When `off_prompt` is set to `False`, the Tool will return its output directly to the LLM.

Lets look at a simple example where `off_prompt` is set to `False`:

```python
--8<-- "docs/griptape-framework/structures/src/task_memory_1.py"
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
--8<-- "docs/griptape-framework/structures/src/task_memory_2.py"
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

When we set `off_prompt` to `True`, the Agent does not function as expected, even generating an error. This is because the Calculator output is being stored in Task Memory but the Agent has no way to access it. 
To fix this, we need a [Tool that can read from Task Memory](#tools-that-can-read-from-task-memory) such as the `TaskMemoryClient`.
This is an example of [not providing a Task Memory compatible Tool](#not-providing-a-task-memory-compatible-tool).

## Task Memory Client

The [TaskMemoryClient](../../griptape-tools/official-tools/task-memory-client.md) is a Tool that allows an Agent to interact with Task Memory. It has the following methods:

- `query`: Retrieve the content of an Artifact stored in Task Memory.
- `summarize`: Summarize the content of an Artifact stored in Task Memory.

Let's add `TaskMemoryClient` to the Agent and run the same task.
Note that on the `TaskMemoryClient` we've set `off_prompt` to `False` so that the results of the query can be returned directly to the LLM. 
If we had kept it as `True`, the results would have been stored back Task Memory which would've put us back to square one. See [Task Memory Looping](#task-memory-looping) for more information on this scenario.

```python
--8<-- "docs/griptape-framework/structures/src/task_memory_3.py"
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

While this fixed the problem, it took a handful more steps than when we just had `Calculator()`. Something like a basic calculation is an instance of where [Task Memory may not be necessary](#task-memory-may-not-be-necessary).
Let's look at a more complex example where Task Memory shines.

## Large Data

Let's say we want to query the contents of a very large webpage.

```python
--8<-- "docs/griptape-framework/structures/src/task_memory_4.py"
```

When running this example, we get the following error:
```
[04/26/24 13:20:02] ERROR    ToolkitTask 67e2f907f95d4850ae79f9da67df54c1
                             Error code: 400 - {'error': {'message': "This model's maximum context length is 8192 tokens. However, your messages resulted in 73874 tokens.
                             Please reduce the length of the messages.", 'type': 'invalid_request_error', 'param': 'messages', 'code': 'context_length_exceeded'}}
```

This is because the content of the webpage is too large to fit in the LLM's input token limit. We can fix this by storing the content in Task Memory, and then querying it with the `TaskMemoryClient`.
Note that we're setting `off_prompt` to `False` on the `TaskMemoryClient` so that the _queried_ content can be returned directly to the LLM.

```python
--8<-- "docs/griptape-framework/structures/src/task_memory_5.py"
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

Here is an example where we use GPT-4 to orchestrate the Tools and store the data in Task Memory, and Amazon Bedrock's Titan model to query the raw content.
In this example, GPT-4 _never_ sees the contents of the page, only that it was stored in Task Memory. Even the query results generated by the Titan model are stored in Task Memory so that the `FileManager` can save the results to disk without GPT-4 ever seeing them.

```python 
--8<-- "docs/griptape-framework/structures/src/task_memory_6.py"
```

```
[06/21/24 16:00:01] INFO     ToolkitTask 17f30ac14701490c8ef71508f420ea9f       
                             Input: Use this page                               
                             https://en.wikipedia.org/wiki/Elden_Ring to find   
                             how many copies of Elden Ring have been sold, and  
                             then save the result to a file.                    
[06/21/24 16:00:05] INFO     Subtask cb06889205334ec9afd7e97f7f231ab5           
                             Thought: First, I need to scrape the content of the
                             provided URL to find the information about how many
                             copies of Elden Ring have been sold. Then, I will  
                             save this information to a file.                   
                                                                                
                             Actions: [{"name": "WebScraper", "path":           
                             "get_content", "input": {"values": {"url":         
                             "https://en.wikipedia.org/wiki/Elden_Ring"}},      
                             "tag": "scrape_elden_ring"}]                       
[06/21/24 16:00:12] INFO     Subtask cb06889205334ec9afd7e97f7f231ab5           
                             Response: Output of "WebScraper.get_content" was   
                             stored in memory with memory_name "TaskMemory" and 
                             artifact_namespace                                 
                             "7e48bcff0da94ad3b06aa4e173f8f37b"                 
[06/21/24 16:00:17] INFO     Subtask 56102d42475d413299ce52a0230506b7           
                             Thought: Now that the webpage content is stored in 
                             memory, I need to query this memory to find the    
                             information about how many copies of Elden Ring    
                             have been sold.                                    
                             Actions: [{"tag": "query_sales", "name":           
                             "TaskMemoryClient", "path": "query", "input":      
                             {"values": {"memory_name": "TaskMemory",           
                             "artifact_namespace":                              
                             "7e48bcff0da94ad3b06aa4e173f8f37b", "query": "How  
                             many copies of Elden Ring have been sold?"}}}]     
[06/21/24 16:00:19] INFO     Subtask 56102d42475d413299ce52a0230506b7           
                             Response: Output of "TaskMemoryClient.query" was   
                             stored in memory with memory_name "TaskMemory" and 
                             artifact_namespace                                 
                             "9ecf4d7b7d0c46149dfc46ba236f178e"                 
[06/21/24 16:00:25] INFO     Subtask ed2921791dcf46b68c9d8d2f8dbeddbd           
                             Thought: Now that I have the sales information     
                             stored in memory, I need to save this information  
                             to a file.                                         
                             Actions: [{"tag": "save_sales_info", "name":       
                             "FileManager", "path":                             
                             "save_memory_artifacts_to_disk", "input":          
                             {"values": {"dir_name": "sales_info", "file_name": 
                             "elden_ring_sales.txt", "memory_name":             
                             "TaskMemory", "artifact_namespace":                
                             "9ecf4d7b7d0c46149dfc46ba236f178e"}}}]             
                    INFO     Subtask ed2921791dcf46b68c9d8d2f8dbeddbd           
                             Response: Successfully saved memory artifacts to   
                             disk                                               
[06/21/24 16:00:27] INFO     ToolkitTask 17f30ac14701490c8ef71508f420ea9f       
                             Output: The information about how many copies of   
                             Elden Ring have been sold has been successfully    
                             saved to the file "elden_ring_sales.txt" in the    
                             "sales_info" directory.
```

## Tools That Can Read From Task Memory

As seen in the previous example, certain Tools are designed to read directly from Task Memory. This means that you can use these Tools to interact with the data stored in Task Memory without needing to pass it through the LLM.

Today, these include:

- [TaskMemoryClient](../../griptape-tools/official-tools/task-memory-client.md)
- [FileManager](../../griptape-tools/official-tools/file-manager.md)
- [AwsS3Client](../../griptape-tools/official-tools/aws-s3-client.md)
- [GoogleDriveClient](../../griptape-tools/official-tools/google-drive-client.md)
- [GoogleDocsClient](../../griptape-tools/official-tools/google-docs-client.md)

## Task Memory Considerations

Task Memory is a powerful feature of Griptape, but with great power comes great responsibility. Here are some things to keep in mind when using Task Memory:

### Tool Return Types 
Griptape will only store Artifacts in Task Memory that have been explicitly defined in the `artifact_storages` parameter of the `TaskMemory` object. 
If you try to store an Artifact that is not defined in `artifact_storages`, Griptape will raise an error. The exception to this is `InfoArtifact`s and `ErrorArtifact`s. Griptape will never store these Artifacts store in Task Memory.
By default, Griptape will store `TextArtifact`'s, `BlobArtifact`'s in Task Memory. Additionally, Griptape will also store the elements of `ListArtifact`'s as long as they are of a supported Artifact type. 

### Not Providing a Task Memory Compatible Tool
When using Task Memory, make sure that you have at least one Tool that can read from Task Memory. If you don't, the data stored in Task Memory will be inaccessible to the Agent and it may hallucinate Tool Activities.

```python
--8<-- "docs/griptape-framework/structures/src/task_memory_7.py"
```

### Task Memory Looping
An improper configuration of Tools can lead to the LLM using the Tools in a loop. For example, if you have a Tool that stores data in Task Memory and another Tool that queries that data from Task Memory ([Tools That Can Read From Task Memory](#tools-that-can-read-from-task-memory)), make sure that the query Tool does not store the data back in Task Memory.
This can create a loop where the same data is stored and queried over and over again.

```python
--8<-- "docs/griptape-framework/structures/src/task_memory_8.py"
```

### Task Memory May Not Be Necessary
Task Memory may not be necessary for all use cases. If the data returned by a Tool is not sensitive, not too large, and does not need to be acted upon by another Tool, you can leave the default of `off_prompt` to `False` and return the data directly to the LLM.

```python
--8<-- "docs/griptape-framework/structures/src/task_memory_9.py"
```

