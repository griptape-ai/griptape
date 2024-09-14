from __future__ import annotations

from attrs import define, field

from griptape.artifacts import BlobArtifact


@define
class ImageArtifact(BlobArtifact):
    """Stores image data.

    Attributes:
        format: The format of the image data. Used when building the MIME type.
        width: The width of the image.
        height: The height of the image
    """

    format: str = field(kw_only=True, metadata={"serializable": True})
    width: int = field(kw_only=True, metadata={"serializable": True})
    height: int = field(kw_only=True, metadata={"serializable": True})

    @property
    def mime_type(self) -> str:
        return f"image/{self.format}"

    def to_bytes(self) -> bytes:
        return self.value

    def to_text(self) -> str:
        return f"Image, format: {self.format}, size: {len(self.value)} bytes"
