## Overview

Building your own tools is easy with Griptape!

To start, create a directory for your tool inside your project. All tool directories should have the following components:

* `tool.py` file with a tool Python class.
* `requirements.txt` file with tool Python dependencies.

Let's build a simple random number generator tool! First, create a new directory for your tool `rng_tool`. This is where all tool files will go.

## Tool Dependencies

To add Python dependencies for your tool, add a `requirements.txt` file. The tool we are building is pretty simple, so you can leave that file empty.

## Tool Implementation

Next, create a `tool.py` file with the following code:

```python
--8<-- "docs/griptape-tools/custom-tools/src/index_1.py"
```

## Testing Custom Tools

Finally, let's test our tool:

```python
--8<-- "docs/griptape-tools/custom-tools/src/index_2.py"
```

That's it! You can start using this tool with any converter or directly via Griptape.

Check out other [Griptape Tools](https://github.com/griptape-ai/griptape/tree/main/griptape/tools) to learn more about tool implementation details.
