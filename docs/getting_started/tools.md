# Tools

The most powerful feature of Warpspeed is the ability of workflow and pipeline prompt steps to generate *chains of thought* and use tools that can interact with the outside world. We use the [ReAct](https://arxiv.org/abs/2210.03629) technique to implement reasoning and acting in the underlying LLMs without using any fine-tuning. There are two types of tool steps that Warpspeed supports:

- `ToolStep` takes one tool as a parameter and passes it to the LLM that decides if it should use it to respond to the prompt.
- `ToolkitStep` takes multiple tools as a parameter, so that the underlying LLM can decide which tool to use for every chain of thought step.

Here is how to use tools:

```python
pipeline = Pipeline()

pipeline.add_steps(
    ToolStep(
        "Research and summarize the most important events of February 2023",
        tool=WikiTool()
    ),
    ToolkitStep(
        "Calculate 3^12 and send an email with the answer and the following text to hello@warpspeed.cc:\n{{ input }}",
        tools=[
            CalculatorTool(),
            EmailSenderTool(
                host="localhost",
                port=1025,
                from_email="hello@warpspeed.cc",
                use_ssl=False
            )
        ],
        id="calc_email"
    )
)

pipeline.run()
```

`ToolStep` instructs an LLM to use a `WikiTool` that provides a JSON schema and *few-shot learning* examples that the LLM is automatically "trained" on to interact with Warpspeed. The LLM can then decide to use a tool to provide a better prompt response by adding substeps that follow the Thought/Action/Observation ReAct routine. For this prompt, it can obviously use a Wiki tool to obtain new information.

`ToolkitStep` works the same way, but it provides multiple tools for the LLM to choose from depending on the task. In our example, the LLM uses `CalculatorTool` to calculate `3^12` and `EmailSenderTool` to send an email.

Warpspeed supports multiple tools and allows you to implement your own.
