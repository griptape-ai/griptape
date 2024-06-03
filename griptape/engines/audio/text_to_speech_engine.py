from __future__ import annotations

from attrs import define, field

from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.drivers import BaseTextToSpeechDriver


@define
class TextToSpeechEngine:
    text_to_speech_driver: BaseTextToSpeechDriver = field(kw_only=True)

    def run(self, prompts: list[str], *args, **kwargs) -> AudioArtifact:
        return self.text_to_speech_driver.try_text_to_audio(prompts=prompts)
