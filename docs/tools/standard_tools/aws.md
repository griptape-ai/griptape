# AwsTool

This tool enables LLMs to run AWS CLI commands. Before using this tool, make sure to [install and configure](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) AWS CLI v2.

```python
ToolStep(
    "show me all of my VPCs",
    tool=AwsTool()
)
```

> **Warning**
> By default, this tool uses `CommandRunner`, which executes commands locally in a subprocess. This is not ideal for production environments, where you generally want to execute arbitrary commands in a container. We are working on adding more command runner options soon.