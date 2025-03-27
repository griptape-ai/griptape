from __future__ import annotations

import logging
from abc import ABC
from typing import Callable, TypeVar, Union

from attrs import define, field

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.configs import Defaults
from griptape.mixins.rule_mixin import RuleMixin
from griptape.tasks import BaseTask
from griptape.utils import J2

logger = logging.getLogger(Defaults.logging_config.logger_name)

T = TypeVar("T", bound=BaseArtifact)


@define
class BaseTextInputTask(RuleMixin, BaseTask[T], ABC):
    DEFAULT_INPUT_TEMPLATE = "{{ args[0] }}"

    _input: Union[str, TextArtifact, Callable[[BaseTask], TextArtifact]] = field(
        default=DEFAULT_INPUT_TEMPLATE,
        alias="input",
    )

    @property
    def input(self) -> TextArtifact:
        if isinstance(self._input, TextArtifact):
            return self._input
        if isinstance(self._input, Callable):
            return self._input(self)
        return TextArtifact(J2().render_from_string(self._input, **self.full_context))

    @input.setter
    def input(self, value: str | TextArtifact | Callable[[BaseTask], TextArtifact]) -> None:
        self._input = value

    def before_run(self) -> None:
        super().before_run()

        logger.info("%s %s\nInput: %s", self.__class__.__name__, self.id, self.input.to_text())

    def after_run(self) -> None:
        super().after_run()

        logger.info(
            "%s %s\nOutput: %s",
            self.__class__.__name__,
            self.id,
            self.output.to_text() if self.output is not None else "",
        )
