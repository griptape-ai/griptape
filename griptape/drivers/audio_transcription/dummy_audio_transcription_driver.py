from typing import Optional

from attrs import define, field
from griptape.artifacts import AudioArtifact, TextArtifact
from griptape.drivers import BaseAudioTranscriptionDriver
from griptape.exceptions import DummyException


@define
class DummyAudioTranscriptionDriver(BaseAudioTranscriptionDriver):
    model: str = field(init=False)

    def try_run(self, audio: AudioArtifact, prompts: Optional[list] = None) -> TextArtifact:
        raise DummyException(__class__.__name__, "try_transcription")
