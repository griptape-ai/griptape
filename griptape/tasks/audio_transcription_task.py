from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.configs.defaults_config import Defaults
from griptape.tasks.base_audio_input_task import BaseAudioInputTask

if TYPE_CHECKING:
    from griptape.artifacts import TextArtifact
    from griptape.drivers import BaseAudioTranscriptionDriver


@define
class AudioTranscriptionTask(BaseAudioInputTask):
    audio_transcription_driver: BaseAudioTranscriptionDriver = field(
        default=Factory(lambda: Defaults.drivers_config.audio_transcription_driver),
        kw_only=True,
    )

    def try_run(self) -> TextArtifact:
        return self.audio_transcription_driver.run(self.input)
