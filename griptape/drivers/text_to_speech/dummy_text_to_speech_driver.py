from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.drivers import BaseTextToSpeechDriver
from griptape.exceptions import DummyError

if TYPE_CHECKING:
    from griptape.artifacts.audio_artifact import AudioArtifact


@define
class DummyTextToSpeechDriver(BaseTextToSpeechDriver):
    model: None = field(init=False, default=None, kw_only=True)

    def try_text_to_audio(self, prompts: list[str]) -> AudioArtifact:
        raise DummyError(__class__.__name__, "try_text_to_audio")
