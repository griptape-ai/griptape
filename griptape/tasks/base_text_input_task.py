from __future__ import annotations

from abc import ABC
from typing import Callable

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.mixins.rule_mixin import RuleMixin
from griptape.tasks import BaseTask
from griptape.utils import J2


@define
class BaseTextInputTask(RuleMixin, BaseTask, ABC):
    DEFAULT_INPUT_TEMPLATE = "{{ args[0] }}"

    _input: str | TextArtifact | Callable[[BaseTask], TextArtifact] = field(
        default=DEFAULT_INPUT_TEMPLATE,
        alias="input",
    )

    @property
    def input(self) -> TextArtifact:
        if isinstance(self._input, TextArtifact):
            return self._input
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            return TextArtifact(J2().render_from_string(self._input, **self.full_context))

    @input.setter
    def input(self, value: str | TextArtifact | Callable[[BaseTask], TextArtifact]) -> None:
        self._input = value

    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info("%s %s\nInput: %s", self.__class__.__name__, self.id, self.input.to_text())

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info("%s %s\nOutput: %s", self.__class__.__name__, self.id, self.output.to_text())
