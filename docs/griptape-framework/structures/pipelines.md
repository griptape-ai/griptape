---
search:
  boost: 2
---

## Overview

A [Pipeline](../../reference/griptape/structures/pipeline.md) is very similar to an [Agent](../../reference/griptape/structures/agent.md), but allows for multiple tasks.

You can access the final output of the Pipeline by using the [output](../../reference/griptape/structures/structure.md#griptape.structures.structure.Structure.output) attribute.

## Context

Pipelines have access to the following [context](../../reference/griptape/structures/pipeline.md#griptape.structures.pipeline.Pipeline.context) variables in addition to the [base context](./tasks.md#context).

- `task_outputs`: dictionary containing mapping of all task IDs to their outputs.
- `parent_output`: output from the parent task if one exists, otherwise `None`.
- `parent`: parent task if one exists, otherwise `None`.
- `child`: child task if one exists, otherwise `None`.

## Pipeline

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/pipelines_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/pipelines_1.txt"
    ```
