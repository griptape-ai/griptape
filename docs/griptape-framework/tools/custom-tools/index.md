## Overview

Building your own tools is easy with Griptape!

Tools are nothing more than Python classes that inherit from [BaseTool](../../../reference/griptape/tools/base_tool.md).
Each method in the class is decorated with an [activity](../../../reference/griptape/utils/decorators.md#griptape.utils.decorators.activity) decorator which informs the LLM how and when it should use that Tool Activity.

## Random Tool

Here is a simple Tool for performing various operations with the `random` module.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/custom-tools/src/index_2.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/custom-tools/logs/index_2.txt"
    ```

### Tool Activities

Activities are actions an LLM can perform with a various Tool. They pair a natural language description with some code to execute. Some examples:

- "Can be used to create a random number" -> `generate_rand_num`
- "Can be used to select a random item from a list" -> `select_rand_item`

Technically, each Activity is a method in the tool class that's decorated with the [activity](../../../reference/griptape/utils/decorators.md#griptape.utils.decorators.activity) decorator.

Griptape will convert the Tool and its Activities into the appropriate format for the LLM to use. You can see the schema for a particular Activity by calling [to_json_schema](../../../reference/griptape/mixins/activity_mixin.md#griptape.mixins.activity_mixin.ActivityMixin.to_activity_json_schema).

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/custom-tools/src/to_json_schema.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/custom-tools/logs/to_json_schema.txt"
    ```

Each Activity takes a `config` keyword argument that contains the configuration for the Activity. The configuration can contain:

- `description` (str): A plain text description of the Activity. Ensure that the description is clear and concise as it will help inform the LLM of when to pick this Activity.
- `schema` (optional): An optional instance of `Schema` that defines the input values to the Activity. This field should be omitted if the Activity does not accept any input values.

### Activity Methods

Activity decorated methods should return an [Artifact](../../data/artifacts.md), though Griptape will automatically convert any other return type to an [InfoArtifact](../../data/artifacts.md#info).

If an Activity's config declares a `schema`, the method should declare parameters using one of the following styles:

- Standard python keyword arguments. See `generate_random_number`.
- `values` (dict): A dictionary of the input values to the Activity. See `select_random_item`.
- `params` (dict): A dictionary that will contain a single key, `values`. See `sample_list`. Other keys may be added in the future, though generally, you should prefer using one of the other styles.

!!! warning

    Do not name any schema fields as `values` or `params`. They are reserved for the Activity method signature.

## Tool Dependencies

Each Tool can also have its own dependencies. You can specify them in a `requirements.txt` file in the tool directory and Griptape will install them during Tool execution.
To start, create a directory for your Tool inside your project. The directory must have the following structure:

```
griptape/tools/calculator/
├── __init__.py
├── requirements.txt # file with tool Python dependencies
└── tool.py # file with tool Python class
```

That's it! Import and use your Tool in your project as you would with any other Griptape Tool.

Check out other [Griptape Tools](https://github.com/griptape-ai/griptape/tree/main/griptape/tools) to learn more about tool implementation details.
