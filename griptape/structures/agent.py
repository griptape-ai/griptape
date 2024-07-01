from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from griptape.tools import BaseTool
from griptape.memory.structure import Run
from griptape.structures import Structure
from griptape.tasks import PromptTask, ToolkitTask
from griptape.common import observable

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define
class Agent(Structure):
    input_template: str = field(default=PromptTask.DEFAULT_INPUT_TEMPLATE)
    tools: list[BaseTool] = field(factory=list, kw_only=True)
    max_meta_memory_entries: Optional[int] = field(default=20, kw_only=True)
    fail_fast: bool = field(default=False, kw_only=True)

    @fail_fast.validator  # pyright: ignore
    def validate_fail_fast(self, _, fail_fast: bool) -> None:
        if fail_fast:
            raise ValueError("Agents cannot fail fast, as they can only have 1 task.")

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if len(self.tasks) == 0:
            if self.tools:
                task = ToolkitTask(
                    self.input_template, tools=self.tools, max_meta_memory_entries=self.max_meta_memory_entries
                )
            else:
                task = PromptTask(self.input_template, max_meta_memory_entries=self.max_meta_memory_entries)

            self.add_task(task)

    @property
    def task(self) -> BaseTask:
        return self.tasks[0]

    def add_task(self, task: BaseTask) -> BaseTask:
        self.tasks.clear()

        task.preprocess(self)

        self.tasks.append(task)

        return task

    def add_tasks(self, *tasks: BaseTask) -> list[BaseTask]:
        if len(tasks) > 1:
            raise ValueError("Agents can only have one task.")
        return super().add_tasks(*tasks)

    @observable
    def try_run(self, *args) -> Agent:
        self.task.execute()

        if self.conversation_memory and self.output is not None:
            if isinstance(self.task.input, tuple):
                input_text = self.task.input[0].to_text()
            else:
                input_text = self.task.input.to_text()

            run = Run(input=input_text, output=self.task.output.to_text())

            self.conversation_memory.add_run(run)

        return self
