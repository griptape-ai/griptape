from __future__ import annotations

from attrs import define, field

from griptape.artifacts import BlobArtifact


@define
class AudioArtifact(BlobArtifact):
    """Stores audio data.

    Attributes:
        format: The audio format, e.g. "wav" or "mp3".
    """

    format: str = field(kw_only=True, metadata={"serializable": True})

    @property
    def mime_type(self) -> str:
        return f"audio/{self.format}"

    def to_bytes(self) -> bytes:
        return self.value

    def to_text(self) -> str:
        return f"Audio, format: {self.format}, size: {len(self.value)} bytes"
