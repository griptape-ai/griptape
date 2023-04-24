from __future__ import annotations
import json
from typing import TYPE_CHECKING
from attr import define, field
from griptape.memory import Run
from griptape.structures import StructureWithMemory
from griptape.tasks import PromptTask
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define
class Agent(StructureWithMemory):
    task: BaseTask = field(default=PromptTask(), kw_only=True)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

        if self.task:
            self.add_task(self.task)

    def add_task(self, task: BaseTask) -> BaseTask:
        self.tasks.clear()

        self.task = task

        task.structure = self

        self.tasks.append(task)

        return task

    def add_tasks(self, *tasks: BaseTask) -> list[BaseTask]:
        raise NotImplementedError("Method is not implemented: agents can only have one task.")

    def prompt_stack(self, task: BaseTask) -> list[str]:
        return self.add_memory_to_prompt_stack(
            super().prompt_stack(task),
            J2("prompts/agent.j2").render(
                has_memory=self.memory is not None,
                task=self.task
            )
        )

    def run(self, *args) -> BaseTask:
        self._execution_args = args

        self.task.reset()

        self.task.execute()

        if self.memory:
            run = Run(
                input=self.task.input.value,
                output=self.task.output.value
            )

            self.memory.add_run(run)

        self._execution_args = ()

        return self.task

    def to_dict(self) -> dict:
        from griptape.schemas import AgentSchema

        return AgentSchema().dump(self)

    @classmethod
    def from_dict(cls, agent_dict: dict) -> Agent:
        from griptape.schemas import AgentSchema

        return AgentSchema().load(agent_dict)

    @classmethod
    def from_json(cls, agent_json: str) -> Agent:
        return Agent.from_dict(json.loads(agent_json))
