## Overview 
A [Pipeline](../../reference/griptape/structures/pipeline.md) is very similar to an [Agent](../../reference/griptape/structures/agent.md), but allows for multiple tasks.

## Context

Pipelines have access to the following [context](../../reference/griptape/structures/pipeline.md#griptape.structures.pipeline.Pipeline.context) variables in addition to the [base context](./tasks.md#context).

* `parent_output`: output from the parent.
* `parent`: parent task.
* `child`: child task.


## Pipeline

```python
from griptape.tasks import PromptTask
from griptape.structures import Pipeline


pipeline = Pipeline()

pipeline.add_tasks(
    # take the first argument from the pipeline `run` method
    PromptTask("{{ args[0] }}"),
    # take the output from the previous task and insert it into the prompt
    PromptTask("Say the following like a pirate: {{ parent_output }}")
)

pipeline.run("Write me a haiku about sailing.")
```

```
[09/08/23 10:18:46] INFO     PromptTask b2d35331b8e5455abbb9567d10044001
                             Input: Write me a haiku about sailing.
[09/08/23 10:18:50] INFO     PromptTask b2d35331b8e5455abbb9567d10044001
                             Output: Sails catch morning breeze,
                             Sea whispers secrets to hull,
                             Horizon awaits.
                    INFO     PromptTask 28e36610063e4d728228a814b48296ef
                             Input: Say the following like a pirate: Sails catch morning breeze,
                             Sea whispers secrets to hull,
                             Horizon awaits.
[09/08/23 10:19:21] INFO     PromptTask 28e36610063e4d728228a814b48296ef
                             Output: Yarr! Th' sails snag th' mornin' zephyr,
                             Th' sea be whisperin' secrets to th' hull,
                             Th' horizon be awaitin', matey.
```
