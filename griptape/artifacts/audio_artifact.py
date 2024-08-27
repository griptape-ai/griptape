from __future__ import annotations

from attrs import define, field

from griptape.artifacts import BaseArtifact


@define
class AudioArtifact(BaseArtifact):
    """Stores audio data.

    Attributes:
        value: The audio data.
        format: The audio format, e.g. "wav" or "mp3".
    """

    value: bytes = field(metadata={"serializable": True})
    format: str = field(kw_only=True, metadata={"serializable": True})

    @property
    def mime_type(self) -> str:
        return f"audio/{self.format}"

    def to_bytes(self) -> bytes:
        return self.value

    def to_text(self) -> str:
        return f"Audio, format: {self.format}, size: {len(self.value)} bytes"
