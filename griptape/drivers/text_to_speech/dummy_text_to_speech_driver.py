from typing import Optional
from attrs import define, field
from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.drivers import BaseTextToSpeechDriver
from griptape.exceptions import DummyException


@define
class DummyTextToSpeechDriver(BaseTextToSpeechDriver):
    model: Optional[str] = field(init=False)

    def __attrs_post_init__(self):
        self.model = None

    def try_text_to_audio(self, prompts: list[str]) -> AudioArtifact:
        raise DummyException(__class__.__name__, "try_text_to_audio")
