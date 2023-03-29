# DataScientistTool

This tool enables LLMs to run more complex calculations in Python. The user can notify the LLM which libraries are available by specifying them in the constructor. By default, only `math` is available.

```python
ToolStep(
    "what's 123^321?",
    tool=DataScientistTool(
        libs={"numpy": "np", "math": "math"}
    )
)
```

This will make `numpy` available as `np` via `import numpy as np` and `math` as `math` via `import math`. Before injecting libraries in the constructor, make sure they are installed in your current environment.

> **Warning**
> By default, this tool uses `PythonRunner`, which executes code locally with sanitized `exec`. This is not ideal for production environments, where you generally want to execute arbitrary code in a container. We are working on adding more code runner options soon.