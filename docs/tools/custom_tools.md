# Custom Tools

Building your own tools is easy with Warpspeed! All you need is a Python class, JSON schema to describe tool actions to the LLM, a set of examples, and a Marshmallow schema for serialization/deserialization. Let's walk through all the required steps and build a simple random number generator tool.

First, create a Python class in a separate directory that generates a random float and optionally truncates it:

```python
import random
from typing import Optional
from warpspeed.tools import Tool


class RandomGenTool(Tool):
    def run(self, num_of_decimals: Optional[int]) -> float:
        if num_of_decimals is None:
            return random.random()
        else:
            return round(random.random(), num_of_decimals)

```

Add a `schema.json` file describing the tool:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "random_gen",
  "description": "This tool can be used to generate random numbers",
  "type": "object",
  "properties": {
    "tool": {
      "type": "string",
      "enum": ["random_gen"]
    },
    "input": {
      "type": "int",
      "description": "The number of decimals to be considered while rounding. Default to null."
    }
  },
  "required": ["tool", "input"]
}
```

Finally, add an `examples.j2` Jinja file with a couple of few-shot learning examples:

```
Input: generate a random number
Thought: I need to use the random_gen tool to answer this question.
Action: {"tool": "random_gen", "input": null}
Observation: 0.8444218515250481
Thought: I have enough information to answer the question
Output: 0.8444218515250481

Input: generate a random number and round it to 2 decimal places
Thought: I need to use the random_gen tool to answer this question.
Action: {"tool": "random_gen", "input": 2}
Observation: 0.14
Thought: I have enough information to answer the question
Output: 0.14
```

Finally, if you want to use `to_json` and `from_json` serialization/deserialization methods, you'll have to add a [Marshmallow](https://marshmallow.readthedocs.io/en/stable/) schema to your tool:

```python
from marshmallow import post_load
from warpspeed.schemas import BaseSchema


class RandomGenToolSchema(BaseSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from .random_gen.random_gen_tool import RandomGenTool

        return RandomGenTool(**data)

```

The schema class has to be in the following format: `<ToolClassName>Schema` and be located in `<tool_class_name>_schema.py`.

Before using the tool, make sure to create an `__init__.py` file in the tool directory with the following contents:

```python
from .random_gen_tool import RandomGenTool
from .random_gen_tool_schema import RandomGenToolSchema

__all__ = [
    "RandomGenTool",
    "RandomGenToolSchema"
]

```

Finally, to use the tool:

```python
from warpspeed.steps import ToolStep
from random_gen.random_gen_tool import RandomGenTool


ToolStep(
    "generate a random number and round it to 3 decimal places",
    tool=RandomGenTool()
)
```

If you are deserializing a workflow or a pipeline from JSON, make sure to specify deserialization schema namespace:

```json
{
  "schema_namespace": "random_gen.random_gen_tool_schema",
  "type": "RandomGenTool"
}
```

Check out other [Warpspeed tools](https://github.com/usewarpspeed/warpspeed/tree/main/warpspeed/tools) to learn more about tools' implementation details. 