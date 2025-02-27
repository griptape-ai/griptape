---
search:
  boost: 2
---

## Overview

A [Ruleset](../../reference/griptape/rules/ruleset.md) can be used to define [Rule](../../reference/griptape/rules/base_rule.md)s for [Structures](../structures/agents.md) and [Tasks](../structures/tasks.md). Griptape places Rules into the LLM's system prompt for strong control over the output.

## Types of Rules

### Rule

[Rule](../../reference/griptape/rules/base_rule.md)s shape the LLM's behavior by defining specific guidelines or instructions for how it should interpret and respond to inputs. Rules can be used to modify language style, tone, or even behavior based on what you define.

!!! tip

    Avoid writing large amounts of text in a single Rule.
    Breaking down your Rules generally helps the LLM follow them more effectively. Additionally, it makes it easier to evaluate the Rule's effectiveness using tools like the [Eval Engine](../engines/eval-engines.md).
    If you have an existing system prompt, consider [overriding the default system prompt](#overriding-system-prompts) instead.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/basic_rule.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/basic_rule.txt"
    ```

### Json Schema

!!! tip

    [Structured Output](../drivers/prompt-drivers.md#structured-output) provides a more robust solution for having the LLM generate structured output.

[JsonSchemaRule](../../reference/griptape/rules/json_schema_rule.md)s defines a structured format for the LLM's output by providing a JSON schema.
This is particularly useful when you need the LLM to return well-formed data, such as JSON objects, with specific fields and data types.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/json_schema_rule.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/json_schema_rule.txt"
    ```

Although Griptape leverages the `schema` library, you're free to use any JSON schema generation library to define your schema!

For example, using `pydantic`:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/json_schema_rule_pydantic.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/json_schema_rule_pydantic.txt"
    ```

## Structure

### Rulesets

You can define a Ruleset at the Structure level if you need to have certain behaviors across all Tasks.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/rulesets_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/rulesets_1.txt"
    ```

### Rules

You can pass [rules](../../reference/griptape/mixins/rule_mixin.md#griptape.mixins.rule_mixin.RuleMixin.rules) directly to the Structure to have a Ruleset created for you.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/rulesets_2.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/rulesets_2.txt"
    ```

## Task

### Rulesets

You can define a Ruleset at the Task level if you need to have different behaviors per Task.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/rulesets_3.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/rulesets_3.txt"
    ```

### Rules

You can pass [rules](../../reference/griptape/mixins/rule_mixin.md#griptape.mixins.rule_mixin.RuleMixin.rules) directly to the Task to have a Ruleset created for you.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/rulesets_4.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/rulesets_4.txt"
    ```

## Overriding System Prompts

While Rulesets are the preferred way to steer LLM output, sometimes you may want to fully override the system prompt.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/generate_system_prompt.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/generate_system_prompt.txt"
    ```

Note that when overriding the system prompt, it is your responsibility to integrate anything that goes in [by default](https://github.com/griptape-ai/griptape/blob/6b31c129fc19a9ba4bdb205ad9e2a40aef9b121f/griptape/tasks/prompt_task.py?plain=1#L216-L221).
You can achieve this by appending the default system prompt to your custom prompt like so:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/structures/src/generate_system_prompt_with_rules.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/structures/logs/generate_system_prompt_with_rules.txt"
    ```
