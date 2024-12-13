from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional, Union

from attrs import Attribute, Factory, define, evolve, field
from schema import Schema

from griptape.artifacts.text_artifact import TextArtifact
from griptape.common import observable
from griptape.configs import Defaults
from griptape.structures import Structure
from griptape.tasks import PromptTask, ToolkitTask

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact
    from griptape.drivers import BasePromptDriver
    from griptape.tasks import BaseTask
    from griptape.tools import BaseTool


@define
class Agent(Structure):
    input: Union[str, list, tuple, BaseArtifact, Callable[[BaseTask], BaseArtifact]] = field(
        default=lambda task: task.full_context["args"][0] if task.full_context["args"] else TextArtifact(value=""),
    )
    stream: bool = field(default=Factory(lambda: Defaults.drivers_config.prompt_driver.stream), kw_only=True)
    prompt_driver: BasePromptDriver = field(
        default=Factory(
            lambda self: evolve(Defaults.drivers_config.prompt_driver, stream=self.stream), takes_self=True
        ),
        kw_only=True,
    )
    tools: list[BaseTool] = field(factory=list, kw_only=True)
    max_meta_memory_entries: Optional[int] = field(default=20, kw_only=True)
    fail_fast: bool = field(default=False, kw_only=True)
    output_type: Optional[Union[type, Schema]] = field(default=None, kw_only=True)

    @fail_fast.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_fail_fast(self, _: Attribute, fail_fast: bool) -> None:  # noqa: FBT001
        if fail_fast:
            raise ValueError("Agents cannot fail fast, as they can only have 1 task.")

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()

        prompt_driver = self.prompt_driver
        prompt_driver.stream = self.stream
        if len(self.tasks) == 0:
            if self.tools:
                task = ToolkitTask(
                    self.input,
                    prompt_driver=prompt_driver,
                    tools=self.tools,
                    max_meta_memory_entries=self.max_meta_memory_entries,
                    output_schema=self._build_schema_from_type(self.output_type)
                    if self.output_type is not None
                    else None,
                )
            else:
                task = PromptTask(
                    self.input,
                    prompt_driver=prompt_driver,
                    max_meta_memory_entries=self.max_meta_memory_entries,
                    output_schema=self._build_schema_from_type(self.output_type)
                    if self.output_type is not None
                    else None,
                )

            self.add_task(task)

    @property
    def task(self) -> BaseTask:
        return self.tasks[0]

    def add_task(self, task: BaseTask) -> BaseTask:
        self._tasks.clear()

        task.preprocess(self)

        self._tasks.append(task)

        return task

    def add_tasks(self, *tasks: BaseTask | list[BaseTask]) -> list[BaseTask]:
        if len(tasks) > 1:
            raise ValueError("Agents can only have one task.")
        return super().add_tasks(*tasks)

    @observable
    def try_run(self, *args) -> Agent:
        self.task.run()

        return self

    def _build_schema_from_type(self, output_type: type | Schema) -> Schema:
        if isinstance(output_type, Schema):
            return output_type
        else:
            return Schema(output_type)
