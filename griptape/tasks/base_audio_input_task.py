from __future__ import annotations

from abc import ABC
from typing import Callable

from attrs import define, field

from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.mixins import RuleMixin
from griptape.tasks import BaseTask


@define
class BaseAudioInputTask(RuleMixin, BaseTask, ABC):
    _input: AudioArtifact | Callable[[BaseTask], AudioArtifact] = field(alias="input")

    @property
    def input(self) -> AudioArtifact:
        if isinstance(self._input, AudioArtifact):
            return self._input
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            raise ValueError("Input must be an AudioArtifact.")

    @input.setter
    def input(self, value: AudioArtifact | Callable[[BaseTask], AudioArtifact]) -> None:
        self._input = value

    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info("%s %s\nInput: %s", self.__class__.__name__, self.id, self.input.to_text())

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info("%s %s\nOutput: %s", self.__class__.__name__, self.id, self.output.to_text())
