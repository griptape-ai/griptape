from __future__ import annotations

import logging
from abc import ABC
from functools import cached_property
from typing import Callable, Union

from attrs import define, field

from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.configs import Defaults
from griptape.mixins.rule_mixin import RuleMixin
from griptape.tasks import BaseTask

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class BaseAudioInputTask(RuleMixin, BaseTask, ABC):
    _input: Union[AudioArtifact, Callable[[BaseTask], AudioArtifact]] = field(alias="input")

    @cached_property
    def input(self) -> AudioArtifact:
        if isinstance(self._input, AudioArtifact):
            return self._input
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            raise ValueError("Input must be an AudioArtifact.")

    def before_run(self) -> None:
        super().before_run()

        logger.info("%s %s\nInput: %s", self.__class__.__name__, self.id, self.input.to_text())

    def after_run(self) -> None:
        super().after_run()

        logger.info("%s %s\nOutput: %s", self.__class__.__name__, self.id, self.output.to_text())
