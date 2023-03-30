# CalculatorTool

This tool enables LLMs to make simple calculations. Here's how to use it:

```python
ToolStep(
    "what's 123^321?",
    tool=CalculatorTool()
)
```

The LLM will be prompted to reason via the Thought/Action/Observation loop to use the calculator and respond with an answer that the calculator provided.

> **Warning**
> By default, this tool uses `PythonRunner`, which executes code locally with sanitized `exec`. This is not ideal for production environments, where you generally want to execute arbitrary code in a container. We are working on adding more code runner options soon.