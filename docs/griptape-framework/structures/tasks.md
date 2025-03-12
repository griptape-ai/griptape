---
search:
  boost: 2
---

## Overview

A [Task](../../reference/griptape/tasks/index.md) is a purpose-built abstraction for the Large Language Model (LLM). Griptape offers various types of Tasks, each suitable for specific use cases.

## Context

Tasks that take input have a field [input](../../reference/griptape/tasks/base_text_input_task.md#griptape.tasks.base_text_input_task.BaseTextInputTask.input) which lets you define the Task objective.
Within the [input](../../reference/griptape/tasks/base_text_input_task.md#griptape.tasks.base_text_input_task.BaseTextInputTask.input), you can access the following [context](../../reference/griptape/structures/structure.md#griptape.structures.structure.Structure.context) variables:

- `args`: an array of arguments passed to the `.run()` method.
- `structure`: the structure that the task belongs to.
- user defined context variables

Additional [context](../../reference/griptape/structures/structure.md#griptape.structures.structure.Structure.context) variables may be added based on the Structure running the task.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/tasks_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/tasks_1.txt"
    ```

## Hooks

All Tasks implement [RunnableMixin](../../reference/griptape/mixins/runnable_mixin.md) which provides `on_before_run` and `on_after_run` hooks for the Task lifecycle.

These hooks can be used to perform actions before and after the Task is run. For example, you can mask sensitive information before running the Task, and transform the output after the Task is run.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/task_hooks.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/task_hooks.txt"
    ```

## Prompt Task

For general-purpose interaction with LLMs, use the [PromptTask](../../reference/griptape/tasks/prompt_task.md):

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/tasks_2.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/tasks_2.txt"
    ```

### Tools

You can pass in one or more Tools which the LLM will decide to use through Chain of Thought (CoT) reasoning. Because tool execution uses CoT, it is recommended to only use with very capable models.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/tasks_4.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/tasks_4.txt"
    ```

#### Reflect On Tool Use

By default, Griptape will pass the results of Tool runs back to the LLM for reflection. This enables the LLM to reason about the results and potentially use additional tools.

However, there may be times where you may want the LLM to give you back the results directly, without reflection.
You can disable this behavior by setting [reflect_on_tool_use](../../reference/griptape/tasks/prompt_task.md#griptape.tasks.prompt_task.PromptTask.reflect_on_tool_use) to `False`.

```python
--8<-- "docs/griptape-framework/structures/src/tasks_reflect_on_tool_use.py"
```

!!! important

    Disabling reflection will prevent the LLM from using one Tool to inform the use of another Tool.
    Instead, you must coordinate the Tool uses yourself.

### Images

If the model supports it, you can also pass image inputs:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/tasks_3.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/tasks_3.txt"
    ```

## Tool Task

!!! warning

    `ToolTask` is deprecated and will be removed in a future version. Use [Prompt Task](./tasks.md#prompt-task) with [reflect_on_tool_use](./tasks.md#reflect-on-tool-use) set to `False` instead.

Another way to use [Griptape Tools](../../griptape-framework/tools/index.md), is with a [Tool Task](../../reference/griptape/tasks/tool_task.md).
This Task takes in a single Tool which the LLM will use without Chain of Thought (CoT) reasoning. Because this Task does not use CoT, it is better suited for less capable models.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/tasks_5.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/tasks_5.txt"
    ```

## Extraction Task

To extract information from text, use an [ExtractionTask](../../reference/griptape/tasks/extraction_task.md).
This Task takes an [Extraction Engine](../../griptape-framework/engines/extraction-engines.md), and a set of arguments specific to the Engine.

### CSV Extraction

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/tasks_6.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/tasks_6.txt"
    ```

### JSON Extraction

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/tasks_7.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/tasks_7.txt"
    ```

## Text Summary Task

To summarize a text, use the [TextSummaryTask](../../reference/griptape/tasks/text_summary_task.md).
This Task takes an [Summarization Engine](../../griptape-framework/engines/summary-engines.md), and a set of arguments to the engine.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/tasks_8.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/tasks_8.txt"
    ```

## RAG Task

To query text, use the [RagTask](../../reference/griptape/tasks/rag_task.md).
This task takes a [RAG Engine](../../griptape-framework/engines/rag-engines.md), and a set of arguments specific to the engine.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/tasks_9.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/tasks_9.txt"
    ```

## Code Execution Task

To execute an arbitrary Python function, use the [CodeExecutionTask](../../reference/griptape/tasks/code_execution_task.md).
This task takes a python function, and authors can elect to return a custom artifact.

In this example, the `generate_title` function combines a hero's name and setting from previous tasks with a random title, returning a `TextArtifact` that contains the generated fantasy title.
The output of this task can then be referenced by subsequent tasks using the `parent_outputs` templating variable, as shown in the final `PromptTask`.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/tasks_10.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/tasks_10.txt"
    ```

## Branch Task

By default, a [Workflow](../structures/workflows.md) will only run a Task when all the Tasks it depends on have finished.

You can make use of [BranchTask](../../reference/griptape/tasks/branch_task.md) in order to tell the Workflow not to run all dependent tasks, but instead to pick and choose one or more paths to go down.

The `BranchTask`'s [on_run](../../reference/griptape/tasks/branch_task.md#griptape.tasks.branch_task.BranchTask.on_run) function can return one of three things:

1. An `InfoArtifact` containing the `id` of the Task to run next.
1. A `ListArtifact` of `InfoArtifact`s containing the `id`s of the Tasks to run next.
1. An _empty_ `ListArtifact` to indicate that no Tasks should be run next.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/branch_task.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/branch_task.txt"
    ```

## Image Generation Tasks

To generate an image, use one of the following [Image Generation Tasks](../../reference/griptape/tasks/index.md). All Image Generation Tasks accept an [Image Generation Driver](../drivers/image-generation-drivers.md).

All successful Image Generation Tasks will always output an [Image Artifact](../data/artifacts.md#image). Each task can be configured to additionally write the generated image to disk by providing either the `output_file` or `output_dir` field. The `output_file` field supports file names in the current directory (`my_image.png`), relative directory prefixes (`images/my_image.png`), or absolute paths (`/usr/var/my_image.png`). By setting `output_dir`, the task will generate a file name and place the image in the requested directory.

### Prompt Image Generation Task

The [Prompt Image Generation Task](../../reference/griptape/tasks/prompt_image_generation_task.md) generates an image from a text prompt.

```python
--8<-- "docs/griptape-framework/structures/src/tasks_11.py"
```

### Variation Image Generation Task

The [Variation Image Generation Task](../../reference/griptape/tasks/variation_image_generation_task.md) generates an image using an input image and a text prompt. The input image is used as a basis for generating a new image as requested by the text prompt.

```python
--8<-- "docs/griptape-framework/structures/src/tasks_12.py"
```

### Inpainting Image Generation Task

The [Inpainting Image Generation Task](../../reference/griptape/tasks/inpainting_image_generation_task.md) generates an image using an input image, a mask image, and a text prompt. The input image will be modified within the bounds of the mask image as requested by the text prompt.

```python
--8<-- "docs/griptape-framework/structures/src/tasks_13.py"
```

### Outpainting Image Generation Task

The [Outpainting Image Generation Task](../../reference/griptape/tasks/outpainting_image_generation_task.md) generates an image using an input image, a mask image, and a text prompt. The input image will be modified outside the bounds of a mask image as requested by the text prompt.

```python
--8<-- "docs/griptape-framework/structures/src/tasks_14.py"
```

## Structure Run Task

The [Structure Run Task](../../reference/griptape/tasks/structure_run_task.md) runs another Structure with a given input.
This Task is useful for orchestrating multiple specialized Structures in a single run. Note that the input to the Task is a tuple of arguments that will be passed to the Structure.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/tasks_16.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/tasks_16.txt"
    ```

## Assistant Task

The [Assistant Task](../../reference/griptape/tasks/assistant_task.md) enables Structures to interact with various "assistant" services using [Assistant Drivers](../../reference/griptape/drivers/assistant/index.md).

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/tasks_assistant.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/tasks_assistant.txt"
    ```

## Text to Speech Task

This Task enables Structures to synthesize speech from text using [Text to Speech Drivers](../../reference/griptape/drivers/text_to_speech/index.md).

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/tasks_17.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/tasks_17.txt"
    ```

## Audio Transcription Task

This Task enables Structures to transcribe speech from text using [Audio Transcription Drivers](../../reference/griptape/drivers/audio_transcription/index.md).

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/tasks_18.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/tasks_18.txt"
    ```
