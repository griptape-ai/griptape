import json
import re

from griptape.structures import Agent
from griptape.tasks import PromptTask
from griptape.tasks.base_task import BaseTask

SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

original_input = None


def on_before_run(task: BaseTask) -> None:
    global original_input

    original_input = task.input.value

    if isinstance(task, PromptTask):
        task.input = SSN_PATTERN.sub("xxx-xx-xxxx", task.input.value)


def on_after_run(task: BaseTask) -> None:
    if task.output is not None:
        task.output.value = json.dumps(
            {"original_input": original_input, "masked_input": task.input.value, "output": task.output.value}, indent=2
        )


agent = Agent(
    tasks=[
        PromptTask(
            "Respond to this user: {{ args[0] }}",
            on_before_run=on_before_run,
            on_after_run=on_after_run,
        )
    ]
)
agent.run("Hello! My favorite color is blue, and my social security number is 123-45-6789.")
