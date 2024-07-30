from __future__ import annotations

from abc import ABC
from typing import Callable

from attrs import Factory, define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.mixins.rule_mixin import RuleMixin
from griptape.tasks import BaseTask
from griptape.utils import J2


@define
class BaseMultiTextInputTask(RuleMixin, BaseTask, ABC):
    DEFAULT_INPUT_TEMPLATE = "{{ args[0] }}"

    _input: tuple[str, ...] | tuple[TextArtifact, ...] | tuple[Callable[[BaseTask], TextArtifact], ...] = field(
        default=Factory(lambda self: (self.DEFAULT_INPUT_TEMPLATE,), takes_self=True),
        alias="input",
    )

    @property
    def input(self) -> ListArtifact:
        if all(isinstance(elem, TextArtifact) for elem in self._input):
            return ListArtifact([artifact for artifact in self._input if isinstance(artifact, TextArtifact)])
        elif all(isinstance(elem, Callable) for elem in self._input):
            return ListArtifact(
                [callable_input(self) for callable_input in self._input if isinstance(callable_input, Callable)]
            )
        else:
            return ListArtifact(
                [
                    TextArtifact(J2().render_from_string(input_template, **self.full_context))
                    for input_template in self._input
                    if isinstance(input_template, str)
                ],
            )

    @input.setter
    def input(
        self,
        value: tuple[str, ...] | tuple[TextArtifact, ...] | tuple[Callable[[BaseTask], TextArtifact], ...],
    ) -> None:
        self._input = value

    def before_run(self) -> None:
        super().before_run()

        joined_input = "\n".join([i.to_text() for i in self.input])
        self.structure.logger.info("%s %s\nInput: %s", self.__class__.__name__, self.id, joined_input)

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info("%s %s\nOutput: %s", self.__class__.__name__, self.id, self.output.to_text())
