from __future__ import annotations

from attrs import define, field

from griptape.artifacts import AudioArtifact
from griptape.drivers.text_to_speech.base_text_to_speech_driver import BaseTextToSpeechDriver


@define
class MockTextToSpeechDriver(BaseTextToSpeechDriver):
    model: str = field(default="test-model", kw_only=True)
    mock_output: str = field(default="mock output", kw_only=True)
    max_characters: int = field(default=100, kw_only=True)

    def try_text_to_audio(self, prompt: str) -> AudioArtifact:
        return AudioArtifact(value=self.mock_output, format="mp3")
