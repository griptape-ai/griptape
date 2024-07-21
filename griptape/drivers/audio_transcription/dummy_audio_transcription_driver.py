from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.drivers import BaseAudioTranscriptionDriver
from griptape.exceptions import DummyError

if TYPE_CHECKING:
    from griptape.artifacts import AudioArtifact, TextArtifact


@define
class DummyAudioTranscriptionDriver(BaseAudioTranscriptionDriver):
    model: str = field(init=False)

    def try_run(self, audio: AudioArtifact, prompts: Optional[list] = None) -> TextArtifact:
        raise DummyError(__class__.__name__, "try_transcription")
