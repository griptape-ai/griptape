## Overview

One of the most powerful features of Griptape is the ability for Toolkit Tasks to generate _chains of thought_ (CoT) and use tools that can interact with the outside world. We use the [ReAct](https://arxiv.org/abs/2210.03629) technique to implement CoT reasoning and acting in the underlying LLMs without using any fine-tuning.

Griptape implements the reasoning loop in the Toolkit Tasks and integrates Griptape Tools natively.

## Tools
Here is an example of a pipeline using tools: 

```python
from griptape.tasks import ToolkitTask
from griptape.structures import Pipeline
from griptape.tools import WebScraper, FileManager, TaskMemoryClient


pipeline = Pipeline()

pipeline.add_tasks(
    ToolkitTask(
        "Load https://www.griptape.ai, summarize it, and store it in a file called griptape.txt", 
        tools=[WebScraper(off_prompt=True), FileManager(off_prompt=True), TaskMemoryClient(off_prompt=False)]
    ),
)

pipeline.run()
```

```
[09/08/23 10:53:56] INFO     ToolkitTask 979d99f68766423ea05b367e951281bc
                             Input: Load https://www.griptape.ai, summarize it, and store it in a file called griptape.txt
[09/08/23 10:54:02] INFO     Subtask 97bd154a71e14a1699f8152e50490a71
                             Thought: The first step is to load the content of the webpage. I can use the WebScraper tool with the get_content
                             activity for this.

                             Action: {"name": "WebScraper", "path": "get_content", "input": {"values": {"url":
                             "https://www.griptape.ai"}}}
[09/08/23 10:54:03] INFO     Subtask 97bd154a71e14a1699f8152e50490a71
                             Response: Output of "WebScraper.get_content" was stored in memory with memory_name "TaskMemory" and
                             artifact_namespace "9eb6f5828cf64356bf323f11d28be27e"
[09/08/23 10:54:09] INFO     Subtask 7ee08458ce154e3d970711b7d3ed79ba
                             Thought: Now that the webpage content is stored in memory, I can use the TaskMemory tool with the summarize
                             activity to summarize the content.
                             Action: {"name": "TaskMemoryClient", "path": "summarize", "input": {"values": {"memory_name": "TaskMemory", "artifact_namespace": "9eb6f5828cf64356bf323f11d28be27e"}}}
[09/08/23 10:54:12] INFO     Subtask 7ee08458ce154e3d970711b7d3ed79ba
                             Response: Griptape is an open source framework that allows developers to build and deploy AI applications
                             using large language models (LLMs). It provides the ability to create conversational and event-driven apps that
                             can access and manipulate data securely. Griptape enforces structures like sequential pipelines and workflows for
                             predictability, while also allowing for creativity by safely prompting LLMs with external APIs and data stores.
                             The framework can be used to create AI systems that operate across both predictability and creativity dimensions.
                             Griptape Cloud is a managed platform for deploying and managing AI apps.
[09/08/23 10:54:24] INFO     Subtask a024949a9a134f058f2e6b7c379c8713
                             Thought: Now that I have the summary, I can store it in a file called griptape.txt. I can use the FileManager
                             tool with the save_file_to_disk activity for this.
                             Action: {"name": "FileManager", "path": "save_file_to_disk", "input": {"values":
                             {"memory_name": "TaskMemory", "artifact_namespace": "9eb6f5828cf64356bf323f11d28be27e", "path":
                             "griptape.txt"}}}
                    INFO     Subtask a024949a9a134f058f2e6b7c379c8713
                             Response: saved successfully
[09/08/23 10:54:27] INFO     ToolkitTask 979d99f68766423ea05b367e951281bc
                             Output: The summary of the webpage https://www.griptape.ai has been successfully stored in a file called
                             griptape.txt.
```
