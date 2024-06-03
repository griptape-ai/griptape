from __future__ import annotations

from abc import ABC
from typing import Callable

from attrs import define, field

from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.engines import AudioTranscriptionEngine
from griptape.artifacts import TextArtifact
from griptape.mixins import RuleMixin
from griptape.tasks import BaseTask


@define
class AudioTranscriptionTask(RuleMixin, BaseTask, ABC):
    _input: AudioArtifact | Callable[[BaseTask], AudioArtifact] = field()
    _audio_transcription_engine: AudioTranscriptionEngine = field(
        default=None, kw_only=True, alias="audio_transcription_engine"
    )

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

    @property
    def audio_transcription_engine(self) -> AudioTranscriptionEngine:
        if self._audio_transcription_engine is None:
            if self.structure is not None:
                self._audio_transcription_engine = AudioTranscriptionEngine(
                    audio_transcription_driver=self.structure.config.audio_transcription_driver
                )
            else:
                raise ValueError("Audio Generation Engine is not set.")
        return self._audio_transcription_engine

    @audio_transcription_engine.setter
    def audio_transcription_engine(self, value: AudioTranscriptionEngine) -> None:
        self._audio_transcription_engine = value

    def run(self) -> TextArtifact:
        return self.audio_transcription_engine.run(self.input)
