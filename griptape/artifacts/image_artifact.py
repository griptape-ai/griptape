from __future__ import annotations

import base64

from attrs import define, field

from griptape.artifacts import BlobArtifact


@define
class ImageArtifact(BlobArtifact):
    """Stores image data.

    Attributes:
        value: The image data.
        format: The format of the image data.
        width: The width of the image.
        height: The height of the image
    """

    value: bytes = field(metadata={"serializable": True})
    format: str = field(kw_only=True, metadata={"serializable": True})
    width: int = field(kw_only=True, metadata={"serializable": True})
    height: int = field(kw_only=True, metadata={"serializable": True})

    @property
    def base64(self) -> str:
        return base64.b64encode(self.value).decode("utf-8")

    @property
    def mime_type(self) -> str:
        return f"image/{self.format}"

    def to_bytes(self) -> bytes:
        return self.value

    def to_text(self) -> str:
        return self.base64
