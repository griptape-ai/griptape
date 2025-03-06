---
search:
  boost: 2
---

## Overview

Task Memory is a powerful feature of Griptape that allows you to control where the data returned by [Tools](../tools/index.md) is stored. This is useful in the following scenarios:

- **Security requirements**: many organizations don't want data to leave their cloud for regulatory and security reasons.
- **Long textual content**: when textual content returned by Tools can't fit in the token limit, it's often useful to perform actions on it as a separate operation, not through the main LLM.
- **Non-textual content**: Tools can generate images, videos, PDFs, and other non-textual content that can be stored in Task Memory and acted upon later by other Tools.

!!! tip

    Running into issue with Task Memory? Check out the [Task Memory Considerations](#task-memory-considerations) section for some common pitfalls.

## Off Prompt

You can enable or disable sending a Tool's results to Task Memory with the `off_prompt` parameter. By default, all Tools have `off_prompt` set to `False` making this an opt-in feature.
When `off_prompt` is set to `True`, the Tool will store its output in Task Memory. When `off_prompt` is set to `False`, the Tool will return its output directly to the LLM.

Lets look at a simple example where `off_prompt` is set to `False`:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/task_memory_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/task_memory_1.txt"
    ```

Since the result of the CalculatorTool Tool is neither sensitive nor too large, we can set `off_prompt` to `False` and not use Task Memory.

Let's explore what happens when `off_prompt` is set to `True`:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/task_memory_2.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/task_memory_2.txt"
    ```

When we set `off_prompt` to `True`, the Agent does not function as expected, even generating an error. This is because the Calculator output is being stored in Task Memory but the Agent has no way to access it.
To fix this, we need a [Tool that can read from Task Memory](#tools-that-can-read-from-task-memory) such as the `PromptSummaryTool`.
This is an example of [not providing a Task Memory compatible Tool](#not-providing-a-task-memory-compatible-tool).

## Prompt Summary Tool

The [PromptSummaryTool](../tools/official-tools/index.md#prompt-summary) is a Tool that allows an Agent to summarize the Artifacts in Task Memory. It has the following methods:

Let's add `PromptSummaryTool` to the Agent and run the same task.
Note that on the `PromptSummaryTool` we've set `off_prompt` to `False` so that the results of the query can be returned directly to the LLM.
If we had kept it as `True`, the results would have been stored back Task Memory which would've put us back to square one. See [Task Memory Looping](#task-memory-looping) for more information on this scenario.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/task_memory_3.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/task_memory_3.txt"
    ```

While this fixed the problem, it took a handful more steps than when we just had `CalculatorTool()`. Something like a basic calculation is an instance of where [Task Memory may not be necessary](#task-memory-may-not-be-necessary).
Let's look at a more complex example where Task Memory shines.

## Large Data

Let's say we want to query the contents of a very large webpage.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/task_memory_4.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/task_memory_4.txt"
    ```

When running this example, we get the following error:

```
[04/26/24 13:20:02] ERROR    PromptTask 67e2f907f95d4850ae79f9da67df54c1
                             Error code: 400 - {'error': {'message': "This model's maximum context length is 8192 tokens. However, your messages resulted in 73874 tokens.
                             Please reduce the length of the messages.", 'type': 'invalid_request_error', 'param': 'messages', 'code': 'context_length_exceeded'}}
```

This is because the content of the webpage is too large to fit in the LLM's input token limit. We can fix this by storing the content in Task Memory, and then querying it with the `QueryTool`.
Note that we're setting `off_prompt` to `False` on the `QueryTool` so that the _queried_ content can be returned directly to the LLM.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/task_memory_5.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/task_memory_5.txt"
    ```

And now we get the expected output.

```
[08/12/24 14:56:29] INFO     Subtask 8669ee523bb64550850566011bcd14e2
                             Response: "Elden Ring" sold 13.4 million copies worldwide by the end of March 2022 and 25 million by June 2024. The downloadable content (DLC)
                             "Shadow of the Erdtree" sold five million copies within three days of its release.
[08/12/24 14:56:30] INFO     PromptTask d3ce58587dc944b0a30a205631b82944
                             Output: Elden Ring sold 13.4 million copies worldwide by the end of March 2022 and 25 million by June 2024.
```

## Sensitive Data

Because Task Memory splits up the storage and retrieval of data, you can use different models for each step.

Here is an example where we use GPT-4 to orchestrate the Tools and store the data in Task Memory, and Anthropic's Claude 3 Haiku model to query the raw content.
In this example, GPT-4 _never_ sees the contents of the page, only that it was stored in Task Memory. Even the query results generated by the Haiku model are stored in Task Memory so that the `FileManagerTool` can save the results to disk without GPT-4 ever seeing them.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/task_memory_6.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/task_memory_6.txt"
    ```

## Tools That Can Read From Task Memory

As seen in the previous example, certain Tools are designed to read directly from Task Memory. This means that you can use these Tools to interact with the data stored in Task Memory without needing to pass it through the LLM.

Today, these include:

- [PromptSummaryTool](../tools/official-tools/index.md#prompt-summary)
- [ExtractionTool](../tools/official-tools/index.md#extraction)
- [RagTool](../tools/official-tools/index.md#rag)
- [FileManagerTool](../tools/official-tools/index.md#file-manager)
- [ImageQueryTool](../tools/official-tools/index.md#image-query)

## Task Memory Considerations

Task Memory is a powerful feature of Griptape, but with great power comes great responsibility. Here are some things to keep in mind when using Task Memory:

### Tool Return Types

Griptape will only store Artifacts in Task Memory that have been explicitly defined in the `artifact_storages` parameter of the `TaskMemory` object.
If you try to store an Artifact that is not defined in `artifact_storages`, Griptape will raise an error. The exception to this is `InfoArtifact`s and `ErrorArtifact`s. Griptape will never store these Artifacts store in Task Memory.
By default, Griptape will store `TextArtifact`'s, `BlobArtifact`'s in Task Memory. Additionally, Griptape will also store the elements of `ListArtifact`'s as long as they are of a supported Artifact type.

### Not Providing a Task Memory Compatible Tool

When using Task Memory, make sure that you have at least one Tool that can read from Task Memory. If you don't, the data stored in Task Memory will be inaccessible to the Agent and it may hallucinate Tool Activities.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/task_memory_7.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/task_memory_7.txt"
    ```

### Task Memory Looping

An improper configuration of Tools can lead to the LLM using the Tools in a loop. For example, if you have a Tool that stores data in Task Memory and another Tool that queries that data from Task Memory ([Tools That Can Read From Task Memory](#tools-that-can-read-from-task-memory)), make sure that the query Tool does not store the data back in Task Memory.
This can create a loop where the same data is stored and queried over and over again.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/task_memory_8.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/task_memory_8.txt"
    ```

### Task Memory May Not Be Necessary

Task Memory may not be necessary for all use cases. If the data returned by a Tool is not sensitive, not too large, and does not need to be acted upon by another Tool, you can leave the default of `off_prompt` to `False` and return the data directly to the LLM.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/task_memory_9.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/task_memory_9.txt"
    ```
