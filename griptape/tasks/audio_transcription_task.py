from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.engines import AudioTranscriptionEngine
from griptape.tasks.base_audio_input_task import BaseAudioInputTask

if TYPE_CHECKING:
    from griptape.artifacts import TextArtifact


@define
class AudioTranscriptionTask(BaseAudioInputTask):
    _audio_transcription_engine: AudioTranscriptionEngine = field(
        default=None,
        kw_only=True,
        alias="audio_transcription_engine",
    )

    @property
    def audio_transcription_engine(self) -> AudioTranscriptionEngine:
        if self._audio_transcription_engine is None:
            if self.structure is not None:
                self._audio_transcription_engine = AudioTranscriptionEngine(
                    audio_transcription_driver=self.structure.config.audio_transcription_driver,
                )
            else:
                raise ValueError("Audio Generation Engine is not set.")
        return self._audio_transcription_engine

    @audio_transcription_engine.setter
    def audio_transcription_engine(self, value: AudioTranscriptionEngine) -> None:
        self._audio_transcription_engine = value

    def run(self) -> TextArtifact:
        return self.audio_transcription_engine.run(self.input)
