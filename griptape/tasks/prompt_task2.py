from __future__ import annotations

from typing import Callable, Generic, TypeVar, Union, overload

from attrs import define, field

from griptape.artifacts import BaseArtifact, ImageArtifact, ListArtifact, TextArtifact
from griptape.tasks import BaseTask
from griptape.utils import J2

T1 = TypeVar("T1", bound=Union[str, TextArtifact])
T2 = TypeVar("T2", bound=ImageArtifact)
T3 = TypeVar("T3", bound=Union[tuple[str, ...], list[str], ListArtifact[Union[TextArtifact, ImageArtifact]]])
T4 = TypeVar(
    "T4",
    bound=Callable[
        ["PromptTask"], Union[TextArtifact, ImageArtifact, ListArtifact[Union[TextArtifact, ImageArtifact]]]
    ],
)

R1 = TypeVar("R1", bound=TextArtifact)
R2 = TypeVar("R2", bound=ImageArtifact)
R3 = TypeVar("R3", bound=ListArtifact[Union[TextArtifact, ImageArtifact]])
R4 = TypeVar("R4", bound=Union[TextArtifact, ImageArtifact, ListArtifact[Union[TextArtifact, ImageArtifact]]])


@define
class PromptTask(BaseTask, Generic[T1, T2, T3, T4, R1, R2, R3, R4]):
    _input: Union[
        T1,
        T2,
        T3,
        T4,
    ] = field(
        alias="input",
    )

    @property
    def input(self) -> R1 | R2 | R3 | R4:
        return self._process_task_input(self._input)

    @input.setter
    def input(
        self,
        value: T1 | T2 | T3 | T4,
    ) -> None:
        self._input = value

    def try_run(self) -> BaseArtifact:
        return TextArtifact("")

    @overload
    def _process_task_input(self, task_input: T1) -> R1: ...

    @overload
    def _process_task_input(self, task_input: T2) -> R2: ...

    @overload
    def _process_task_input(self, task_input: T3) -> R3: ...

    @overload
    def _process_task_input(
        self,
        task_input: T4,
    ) -> R4: ...

    def _process_task_input(
        self,
        task_input: T1 | T2 | T3 | T4,
    ) -> R1 | R2 | R3 | R4:
        if isinstance(task_input, TextArtifact):
            task_input.value = J2().render_from_string(task_input.value, **self.full_context)

            return task_input
        elif isinstance(task_input, Callable):
            return self._process_task_input(task_input(self))
        elif isinstance(task_input, ListArtifact):
            return ListArtifact([self._process_task_input(elem) for elem in task_input.value])
        elif isinstance(task_input, BaseArtifact):
            return task_input
        elif isinstance(task_input, (list, tuple)):
            return ListArtifact([self._process_task_input(elem) for elem in task_input])
        else:
            return self._process_task_input(TextArtifact(task_input))
