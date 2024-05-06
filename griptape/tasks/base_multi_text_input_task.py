from __future__ import annotations

from abc import ABC
from typing import Callable

from attr import define, field, Factory

from griptape.artifacts import TextArtifact
from griptape.mixins.rule_mixin import RuleMixin
from griptape.tasks import BaseTask
from griptape.utils import J2


@define
class BaseMultiTextInputTask(RuleMixin, BaseTask, ABC):
    DEFAULT_INPUT_TEMPLATE = "{{ args[0] }}"

    _input: tuple[str, ...] | tuple[TextArtifact, ...] | tuple[Callable[[BaseTask], TextArtifact], ...] = field(
        default=Factory(lambda self: (self.DEFAULT_INPUT_TEMPLATE,), takes_self=True), alias="input"
    )

    @property
    def input(self) -> tuple[TextArtifact, ...]:
        if all(isinstance(elem, TextArtifact) for elem in self._input):
            return self._input  # pyright: ignore
        elif all(isinstance(elem, Callable) for elem in self._input):
            return tuple([elem(self) for elem in self._input])  # pyright: ignore
        elif isinstance(self._input, tuple):
            return tuple(
                [
                    TextArtifact(J2().render_from_string(input_template, **self.full_context))  # pyright: ignore
                    for input_template in self._input
                ]
            )
        else:
            return tuple([TextArtifact(J2().render_from_string(self._input, **self.full_context))])

    @input.setter
    def input(
        self, value: tuple[str, ...] | tuple[TextArtifact, ...] | tuple[Callable[[BaseTask], TextArtifact], ...]
    ) -> None:
        self._input = value

    def before_run(self) -> None:
        super().before_run()

        joined_input = "\n".join([input.to_text() for input in self.input])
        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nInput: {joined_input}")

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nOutput: {self.output.to_text()}")
