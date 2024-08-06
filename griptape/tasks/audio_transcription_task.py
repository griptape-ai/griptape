from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.engines import AudioTranscriptionEngine
from griptape.tasks.base_audio_input_task import BaseAudioInputTask

if TYPE_CHECKING:
    from griptape.artifacts import TextArtifact


@define
class AudioTranscriptionTask(BaseAudioInputTask):
    audio_transcription_engine: AudioTranscriptionEngine = field(
        default=Factory(lambda: AudioTranscriptionEngine()),
        kw_only=True,
    )

    def run(self) -> TextArtifact:
        return self.audio_transcription_engine.run(self.input)
