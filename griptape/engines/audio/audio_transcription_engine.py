from attrs import Factory, define, field

from griptape.artifacts import AudioArtifact, TextArtifact
from griptape.config import Config
from griptape.drivers import BaseAudioTranscriptionDriver


@define
class AudioTranscriptionEngine:
    audio_transcription_driver: BaseAudioTranscriptionDriver = field(
        default=Factory(lambda: Config.audio_transcription_driver), kw_only=True
    )

    def run(self, audio: AudioArtifact, *args, **kwargs) -> TextArtifact:
        return self.audio_transcription_driver.try_run(audio)
