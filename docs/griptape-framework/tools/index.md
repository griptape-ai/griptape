# Tools in Griptape

## Overview

One of the most powerful features of Griptape is the ability to use tools that interact with the outside world. Tools give the LLM abilities to invoke APIs, reference data sets, and expand their capabilities beyond simple text generation.

Many of our [Prompt Drivers](../drivers/prompt-drivers.md) leverage the native function calling built into LLMs. For models that do not support this, Griptape provides its own implementation using the [ReAct](https://arxiv.org/abs/2210.03629) technique.

You can switch between these strategies by setting `use_native_tools` to `True` (LLM-native tool calling) or `False` (Griptape tool calling) on your [Prompt Driver](../drivers/prompt-drivers.md).

## Custom Tools

See [Custom Tools](./custom-tools/index.md) for more information on building your own tools.

## Tool Output and Task Memory

Output artifacts from all tool activities (except `InfoArtifact` and `ErrorArtifact`) are stored in short-term `TaskMemory`. To disable this behavior, set the `off_prompt` tool parameter to `False`.

## Using Tools in Pipelines

Griptape provides a set of official tools for accessing and processing data. You can also [build your own tools](./custom-tools/index.md).

Here is an example of a Pipeline using tools:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/src/index_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/logs/index_1.txt"
    ```
