from __future__ import annotations

from typing import Optional

from attrs import define, field

from griptape.artifacts import AudioArtifact, TextArtifact
from griptape.drivers.audio_transcription.base_audio_transcription_driver import BaseAudioTranscriptionDriver


@define
class MockAudioTranscriptionDriver(BaseAudioTranscriptionDriver):
    model: str = field(default="test-model", kw_only=True)
    mock_output: str = field(default="mock output", kw_only=True)

    def try_run(self, audio: AudioArtifact, prompts: Optional[list] = None) -> TextArtifact:
        return TextArtifact(value=self.mock_output)
