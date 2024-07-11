from __future__ import annotations

from attrs import define, field

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from griptape.drivers import BaseTextToSpeechDriver
    from griptape.artifacts.audio_artifact import AudioArtifact


@define
class TextToSpeechEngine:
    text_to_speech_driver: BaseTextToSpeechDriver = field(kw_only=True)

    def run(self, prompts: list[str], *args, **kwargs) -> AudioArtifact:
        return self.text_to_speech_driver.try_text_to_audio(prompts=prompts)
