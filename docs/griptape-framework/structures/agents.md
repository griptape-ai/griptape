---
search:
  boost: 2 
---

## Overview

An [Agent](../../reference/griptape/structures/agent.md) is the quickest way to get started with Griptape.
Agents take in [tools](../../reference/griptape/structures/agent.md#griptape.structures.agent.Agent.tools) and [input](../../reference/griptape/structures/agent.md#griptape.structures.agent.Agent.input)
directly, which the agent uses to dynamically determine whether to use a [Prompt Task](./tasks.md#prompt-task) or [Toolkit Task](./tasks.md#toolkit-task).

If [tools](../../reference/griptape/structures/agent.md#griptape.structures.agent.Agent.tools) are passed provided to the Agent, a [Toolkit Task](./tasks.md#toolkit-task) will be used. If no [tools](../../reference/griptape/structures/agent.md#griptape.structures.agent.Agent.tools)
are provided, a [Prompt Task](./tasks.md#prompt-task) will be used.

You can access the final output of the Agent by using the [output](../../reference/griptape/structures/agent.md#griptape.structures.structure.Structure.output) attribute.

## Toolkit Task Agent

```python
from griptape.tools import Calculator
from griptape.structures import Agent


agent = Agent(
    input="Calculate the following: {{ args[0] }}",
    tools=[Calculator()]
)

agent.run("what's 13^7?")
print("Answer:", agent.output)
```

```
[07/23/24 10:53:41] INFO     ToolkitTask 487db777bc014193ba90b061451b69a6
                             Input: Calculate the following: what's 13^7?
[07/23/24 10:53:42] INFO     Subtask 126cefa3ac5347b88495e25af52f3268
                             Actions: [
                               {
                                 "tag": "call_ZSCH6vNoycOgtPJH2DL2U9ji",
                                 "name": "Calculator",
                                 "path": "calculate",
                                 "input": {
                                   "values": {
                                     "expression": "13**7"
                                   }
                                 }
                               }
                             ]
                    INFO     Subtask 126cefa3ac5347b88495e25af52f3268
                             Response: 62748517
[07/23/24 10:53:43] INFO     ToolkitTask 487db777bc014193ba90b061451b69a6
                             Output: 62,748,517
Answer: 62,748,517
```

## Prompt Task Agent

```python
from griptape.structures import Agent
from griptape.tasks import PromptTask


agent = Agent()
agent.add_task(
    PromptTask(
        "Write me a {{ creative_medium }} about {{ args[0] }} and {{ args[1] }}",
        context={
            'creative_medium': 'haiku'
        }
    )
)

agent.run("Skateboards", "Programming")
```

```
[09/08/23 10:10:24] INFO     PromptTask e70fb08090b24b91a9307fa83479e851
                             Input: Write me a haiku about Skateboards and Programming
[09/08/23 10:10:28] INFO     PromptTask e70fb08090b24b91a9307fa83479e851
                             Output: Code on wheels in flight,
                             Skateboards meet algorithms bright,
                             In binary, we ignite.
```
