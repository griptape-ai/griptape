from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from griptape.core import BaseTool
from griptape.memory.structure import Run, ConversationMemory
from griptape.structures import StructureWithMemory
from griptape.tasks import PromptTask, ToolkitTask
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define
class Agent(StructureWithMemory):
    prompt_template: str = field(default=PromptTask.DEFAULT_PROMPT_TEMPLATE)
    memory: Optional[ConversationMemory] = field(
        default=Factory(lambda: ConversationMemory()),
        kw_only=True
    )
    tools: list[BaseTool] = field(factory=list, kw_only=True)

    def __attrs_post_init__(self) -> None:
        if self.tools:
            task = ToolkitTask(
                self.prompt_template,
                tools=self.tools
            )
        else:
            task = PromptTask(
                self.prompt_template
            )

        self.add_task(task)

        super().__attrs_post_init__()

    @property
    def task(self) -> BaseTask:
        return self.tasks[0]

    def add_task(self, task: BaseTask) -> BaseTask:
        self.tasks.clear()

        self._init_task(task)

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
                input=self.task.input.to_text(),
                output=self.task.output.to_text()
            )

            self.memory.add_run(run)

        self._execution_args = ()

        return self.task
