from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from attrs import Attribute, define, field

from griptape.artifacts.text_artifact import TextArtifact
from griptape.structures import Structure
from griptape.tasks import PromptTask, ToolkitTask

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact
    from griptape.tasks import BaseTask
    from griptape.tools import BaseTool


@define
class Agent(Structure):
    input: str | list | tuple | BaseArtifact | Callable[[BaseTask], BaseArtifact] = field(
        default=lambda task: task.full_context["args"][0] if task.full_context["args"] else TextArtifact(value=""),
    )
    tools: list[BaseTool] = field(factory=list, kw_only=True)
    max_meta_memory_entries: Optional[int] = field(default=20, kw_only=True)
    fail_fast: bool = field(default=False, kw_only=True)
    task: Optional[BaseTask] = field(default=None, kw_only=True)

    _has_default_task: bool = field(default=False, init=False, kw_only=True)

    @fail_fast.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_fail_fast(self, _: Attribute, fail_fast: bool) -> None:  # noqa: FBT001
        if fail_fast:
            raise ValueError("Agents cannot fail fast, as they can only have 1 task.")

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()

        if self.task is None:
            if self.tools:
                self.task = ToolkitTask(
                    self.input, tools=self.tools, max_meta_memory_entries=self.max_meta_memory_entries
                )
            else:
                self.task = PromptTask(self.input, max_meta_memory_entries=self.max_meta_memory_entries)
            self._has_default_task = True

    @property
    def task_graph(self) -> dict[BaseTask, set[BaseTask]]:
        return {self.task: set()} if self.task else {}

    @property
    def tasks(self) -> list[BaseTask]:
        return [self.task] if self.task else []

    def add_task(self, task: Optional[BaseTask], **kwargs) -> Agent:
        if task is None:
            raise ValueError("Task must be provided.")
        self.task = task
        return self

    def add_tasks(self, *tasks: BaseTask, **kwargs) -> Structure:
        if len(tasks) > 1:
            raise ValueError("Agents can only have 1 task.")
        return self.add_task(tasks[0]) if tasks else self
