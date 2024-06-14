from __future__ import annotations

from abc import ABC
from typing import Callable
from collections.abc import Sequence

from attrs import define, field

from griptape.artifacts import TextArtifact, BaseArtifact, ListArtifact
from griptape.mixins.rule_mixin import RuleMixin
from griptape.tasks import BaseTask
from griptape.utils import J2


@define
class BaseTextInputTask(RuleMixin, BaseTask, ABC):
    DEFAULT_INPUT_TEMPLATE = "{{ args[0] }}"

    _input: str | list | tuple | BaseArtifact | Callable[[BaseTask], BaseArtifact] = field(
        default=DEFAULT_INPUT_TEMPLATE, alias="input"
    )

    @property
    def input(self) -> BaseArtifact:
        if isinstance(self._input, list) or isinstance(self._input, tuple):
            artifacts = [self._process_task_input(input) for input in self._input]
            flattened_artifacts = self.__flatten_artifacts(artifacts)

            return ListArtifact(flattened_artifacts)
        else:
            return self._process_task_input(self._input)

    @input.setter
    def input(self, value: str | list | tuple | BaseArtifact | Callable[[BaseTask], BaseArtifact]) -> None:
        self._input = value

    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nInput: {self.input.to_text()}")

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nOutput: {self.output.to_text()}")

    def _process_task_input(
        self, task_input: str | list | BaseArtifact | Callable[[BaseTask], BaseArtifact]
    ) -> BaseArtifact:
        if isinstance(task_input, TextArtifact):
            task_input.value = J2().render_from_string(task_input.value, **self.full_context)

            return task_input
        elif isinstance(task_input, Callable):
            return self._process_task_input(task_input(self))
        elif isinstance(task_input, str):
            return self._process_task_input(TextArtifact(task_input))
        elif isinstance(task_input, BaseArtifact):
            return task_input
        elif isinstance(task_input, list):
            return ListArtifact([self._process_task_input(elem) for elem in task_input])
        else:
            raise ValueError(f"Invalid input type: {type(task_input)} ")

    def __flatten_artifacts(self, artifacts: Sequence[BaseArtifact]) -> Sequence[BaseArtifact]:
        result = []

        for elem in artifacts:
            if isinstance(elem, ListArtifact):
                result.extend(self.__flatten_artifacts(elem.value))
            else:
                result.append(elem)

        return result
