from __future__ import annotations

from typing import TYPE_CHECKING, Union

from attrs import define, field, Factory

from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.drivers import BaseTextToSpeechDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from elevenlabs.client import ElevenLabs

if TYPE_CHECKING:
    import elevenlabs
    import elevenlabs.client


@define
class ElevenLabsTextToSpeechDriver(BaseTextToSpeechDriver):
    api_key: str = field(kw_only=True, metadata={"serializable": True})
    model: Union[str, elevenlabs.Model] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )
    client: elevenlabs.client.ElevenLabs = field(
        default=Factory(
            lambda self: import_optional_dependency("elevenlabs.client").ElevenLabs(api_key=self.api_key),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    voice: Union[str, elevenlabs.Voice] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )
    output_format: str = field(default="mp3_44100_128", kw_only=True, metadata={"serializable": True})
    max_characters: int = field(default=10_000, kw_only=True, metadata={"serializable": True})

    def try_text_to_audio(self, prompt: str) -> AudioArtifact:
        kwargs = {}
        if self.model is not None:
            kwargs["model"] = self.model
        if self.voice is not None:
            kwargs["voice"] = self.voice
        if self.output_format is not None:
            kwargs["output_format"] = self.output_format

        audio = self.client.generate(
            text=prompt,
            **kwargs,
        )

        content = b""
        for chunk in audio:
            content += chunk

        # All ElevenLabs audio format strings have the following structure:
        # {format}_{sample_rate}_{bitrate}
        artifact_format = self.output_format.split("_")[0]

        return AudioArtifact(value=content, format=artifact_format)
