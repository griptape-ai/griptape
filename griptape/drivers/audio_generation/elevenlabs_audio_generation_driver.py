from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any

from attr import define, field, Factory

from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.drivers.audio_generation.base_audio_generation_driver import BaseAudioGenerationDriver
from elevenlabs.client import ElevenLabs
from elevenlabs import play


@define
class ElevenLabsAudioGenerationDriver(BaseAudioGenerationDriver):
    api_key: str = field(kw_only=True, metadata={"serializable": True})
    client: Any = field(
        default=Factory(lambda self: ElevenLabs(api_key=self.api_key), takes_self=True),
        kw_only=True,
        metadata={"serializable": True},
    )
    voice: str = field(kw_only=True, metadata={"serializable": True})

    def try_text_to_audio(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> AudioArtifact:
        audio = self.client.generate(text=prompts[0], voice="Rachel", model="eleven_multilingual_v2")

        play(audio)

        return AudioArtifact(value=audio, format="wav", width=0, height=0)
