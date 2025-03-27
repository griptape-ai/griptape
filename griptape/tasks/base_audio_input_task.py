from __future__ import annotations

import logging
from abc import ABC
from typing import Callable, TypeVar, Union

from attrs import define, field

from griptape.artifacts import AudioArtifact, BaseArtifact
from griptape.configs import Defaults
from griptape.mixins.rule_mixin import RuleMixin
from griptape.tasks import BaseTask

logger = logging.getLogger(Defaults.logging_config.logger_name)

T = TypeVar("T", bound=BaseArtifact)


@define
class BaseAudioInputTask(RuleMixin, BaseTask[T], ABC):
    _input: Union[AudioArtifact, Callable[[BaseTask], AudioArtifact]] = field(alias="input")

    @property
    def input(self) -> AudioArtifact:
        if isinstance(self._input, AudioArtifact):
            return self._input
        if isinstance(self._input, Callable):
            return self._input(self)
        raise ValueError("Input must be an AudioArtifact.")

    @input.setter
    def input(self, value: AudioArtifact | Callable[[BaseTask], AudioArtifact]) -> None:
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
