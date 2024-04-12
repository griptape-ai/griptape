## Overview

An [Agent](../../reference/griptape/structures/agent.md) is the quickest way to get started with Griptape.
Agents take in [tools](../../reference/griptape/structures/agent.md#griptape.structures.agent.Agent.tools) and [input_template](../../reference/griptape/structures/agent.md#griptape.structures.agent.Agent.input_template)
directly, which the agent uses to dynamically determine whether to use a [Prompt Task](./tasks.md#prompt-task) or [Toolkit Task](./tasks.md#toolkit-task).

If [tools](../../reference/griptape/structures/agent.md#griptape.structures.agent.Agent.tools) are passed provided to the Agent, a [Toolkit Task](./tasks.md#toolkit-task) will be used. If no [tools](../../reference/griptape/structures/agent.md#griptape.structures.agent.Agent.tools)
are provided, a [Prompt Task](./tasks.md#prompt-task) will be used.

## Toolkit Task Agent

```python
from griptape.tools import Calculator
from griptape.structures import Agent


agent = Agent(
    input_template="Calculate the following: {{ args[0] }}",
    tools=[Calculator()]
)

agent.run("what's 123^312?")
```

```
[09/08/23 10:11:31] INFO     ToolkitTask 319f53af2e564c15a3b97992fc039ec9
                             Input: Calculate the following: what's 123^312?
[09/08/23 10:11:55] INFO     Subtask cbd5bb8684ad4fc59958201efbf14743
                             Thought: The user wants to calculate the value of 123 raised to the power of 312. I can use the Calculator tool
                             to perform this calculation.

                             Action: {"name": "Calculator", "path": "calculate", "input": {"values": {"expression":
                             "123**312"}}}
                    INFO     Subtask cbd5bb8684ad4fc59958201efbf14743
                             Response:
                             11230388208945295722090491952733133124202871121067044284403441616854053130045246777417573635449877716182202751456
                             62903768337745814236262209544548389555407097435988334710646912635818793342584092805141253230302226219003560706069
                             42457739968799225811781682901969575983855664495472037997890318771511185547708335412624757899597237206373758262442
                             72269858013479598852506666010704868797813623903160430655651532132073996589276408598241791795573009265505912300559
                             47848517605515539611362917584666826953065776743002119105282582194109888263281423789852046556346579319777145449509
                             5671672325351081760983520684046903739998382099007883142337182654942065184263509761170721
[09/08/23 10:12:22] INFO     ToolkitTask 319f53af2e564c15a3b97992fc039ec9
                             Output: The result of 123 raised to the power of 312 is
                             11230388208945295722090491952733133124202871121067044284403441616854053130045246777417573635449877716182202751456
                             62903768337745814236262209544548389555407097435988334710646912635818793342584092805141253230302226219003560706069
                             42457739968799225811781682901969575983855664495472037997890318771511185547708335412624757899597237206373758262442
                             72269858013479598852506666010704868797813623903160430655651532132073996589276408598241791795573009265505912300559
                             47848517605515539611362917584666826953065776743002119105282582194109888263281423789852046556346579319777145449509
                             5671672325351081760983520684046903739998382099007883142337182654942065184263509761170721.
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
