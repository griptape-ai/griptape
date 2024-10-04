## Overview

Building your own tools is easy with Griptape!

To start, you can define your tool in a single Python file within your project. All tool files should have the necessary components in one place, keeping things simple.

* **Optional**: You can include a `requirements.txt` file with Python dependencies if needed. If you do, both the tool file and the `requirements.txt` file must be placed in their own directory together. Griptape will automatically install those dependencies when the tool is loaded.

Let's build a simple random number generator tool! You can define the tool directly in your code.

## Tool Dependencies
If your tool has specific Python dependencies, you can create a requirements.txt file. Although our example is simple and doesn't need it, remember that the requirements.txt file and the tool file must be in a directory together, and Griptape will handle the installation.

## Tool Implementation

Here’s an example of the tool implementation in a single file:

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
