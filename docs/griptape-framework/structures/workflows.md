---
search:
  boost: 2
---

## Overview

A [Workflow](../../reference/griptape/structures/workflow.md) is a non-sequential DAG that can be used for complex concurrent scenarios with tasks having multiple inputs.

You can access the final output of the Workflow by using the [output](../../reference/griptape/structures/structure.md#griptape.structures.structure.Structure.output) attribute.

## Context

Workflows have access to the following [context](../../reference/griptape/structures/workflow.md#griptape.structures.workflow.Workflow.context) variables in addition to the [base context](./tasks.md#context):

- `task_outputs`: dictionary containing mapping of all task IDs to their outputs.
- `parent_outputs`: dictionary containing mapping of parent task IDs to their outputs.
- `parents_output_text`: string containing the concatenated outputs of all parent tasks.
- `parents`: dictionary containing mapping of parent task IDs to their task objects.
- `children`: dictionary containing mapping of child task IDs to their task objects.

## Workflow

Let's build a simple workflow. Let's say, we want to write a story in a fantasy world with some unique characters. We could setup a workflow that generates a world based on some keywords. Then we pass the world description to any number of child tasks that create characters. Finally, the last task pulls in information from all parent tasks and writes up a short story.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/workflows_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/workflows_1.txt"
    ```

Note that we use the `StructureVisualizer` to get a visual representation of the workflow. If we visit the printed url, it should look like this:

![Workflow](https://mermaid.ink/img/Z3JhcGggVEQ7OwoJd29ybGQtLT4gc3RvcnkgJiBzY290dHkgJiBhbm5pZTsKCXNjb3R0eS0tPiBzdG9yeTsKCWFubmllLS0+IHN0b3J5Ow==)

!!! Info

    Output edited for brevity

### Declarative vs Imperative Syntax

The above example showed how to create a workflow using the declarative syntax via the `parent_ids` init param, but there are a number of declarative and imperative options for you to choose between. There is no functional difference, they merely exist to allow you to structure your code as is most readable for your use case. Possibilities are illustrated below.

Declaratively specify parents (same as above example):

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/workflows_2.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/workflows_2.txt"
    ```

Declaratively specify children:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/workflows_3.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/workflows_3.txt"
    ```

Declaratively specifying a mix of parents and children:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/workflows_4.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/workflows_4.txt"
    ```

Imperatively specify parents:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/workflows_5.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/workflows_5.txt"
    ```

Imperatively specify children:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/workflows_6.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/workflows_6.txt"
    ```

Imperatively specify a mix of parents and children:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/workflows_7.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/workflows_7.txt"
    ```

Or even mix imperative and declarative:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/workflows_8.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/workflows_8.txt"
    ```

### Insert Parallel Tasks

`Workflow.insert_tasks()` provides a convenient way to insert parallel tasks between parents and children.

!!! info

    By default, all children are removed from the parent task and all parent tasks are removed from the child task. If you want to keep these parent-child relationships, then set the `preserve_relationship` parameter to `True`.

Imperatively insert parallel tasks between a parent and child:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/workflows_9.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/workflows_9.txt"
    ```

output:

### Bitshift Composition

Task relationships can also be set up with the Python bitshift operators `>>` and `<<`. The following statements are all functionally equivalent:

```python
task1 >> task2
task1.add_child(task2)

task2 << task1
task2.add_parent(task1)

task3 >> [task4, task5]
task3.add_children([task4, task5])
```

When using the bitshift to compose operators, the relationship is set in the direction that the bitshift operator points.
For example, `task1 >> task2` means that `task1` runs first and `task2` runs second.
Multiple operators can be composed – keep in mind the chain is executed left-to-right and the rightmost object is always returned. For example:

```python
task1 >> task2 >> task3 << task4
```

is equivalent to:

```python
task1.add_child(task2)
task2.add_child(task3)
task3.add_parent(task4)
```
