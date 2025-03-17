from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Union

from attrs import define, field

from griptape.artifacts import BaseArtifact, ListArtifact, TextArtifact
from griptape.tasks.base_task import BaseTask
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.drivers.structure_run.base_structure_run_driver import BaseStructureRunDriver


@define
class StructureRunTask(BaseTask):
    """Task to run a Structure.

    Attributes:
        structure_run_driver: Driver to run the Structure.
    """

    _input: Union[str, list, tuple, BaseArtifact, Callable[[BaseTask], BaseArtifact]] = field(
        default=lambda task: task.full_context["args"][0] if task.full_context["args"] else TextArtifact(value=""),
    )

    @property
    def input(self) -> BaseArtifact:
        return self._process_task_input(self._input)

    @input.setter
    def input(self, value: str | list | tuple | BaseArtifact | Callable[[BaseTask], BaseArtifact]) -> None:
        self._input = value

    structure_run_driver: BaseStructureRunDriver = field(kw_only=True)

    def try_run(self) -> BaseArtifact:
        if isinstance(self.input, ListArtifact):
            return self.structure_run_driver.run(*self.input.value)
        return self.structure_run_driver.run(self.input)

    def _process_task_input(
        self,
        task_input: str | tuple | list | BaseArtifact | Callable[[BaseTask], BaseArtifact],
    ) -> BaseArtifact:
        if isinstance(task_input, TextArtifact):
            task_input.value = J2().render_from_string(task_input.value, **self.full_context)

            return task_input
        if isinstance(task_input, Callable):
            return self._process_task_input(task_input(self))
        if isinstance(task_input, ListArtifact):
            return ListArtifact([self._process_task_input(elem) for elem in task_input.value])
        if isinstance(task_input, BaseArtifact):
            return task_input
        if isinstance(task_input, (list, tuple)):
            return ListArtifact([self._process_task_input(elem) for elem in task_input])
        return self._process_task_input(TextArtifact(task_input))
