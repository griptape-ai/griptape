from attrs import define, field
from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.drivers import BaseTextToSpeechDriver
from griptape.exceptions import DummyException


@define
class DummyTextToSpeechDriver(BaseTextToSpeechDriver):
    model: None = field(init=False, default=None, kw_only=True)

    def try_text_to_audio(self, prompts: list[str]) -> AudioArtifact:
        raise DummyException(__class__.__name__, "try_text_to_audio")
