from __future__ import annotations
from typing import Optional
from attr import define, field
from griptape.artifacts import BlobArtifact
import base64


@define(frozen=True)
class ImageArtifact(BlobArtifact):
    """ImageArtifact is a type of BlobArtifact that represents an image.

    Attributes:
        value: Raw bytes representing the image.
        name: Artifact name, generated using creation time and a random string.
        mime_type: The mime type of the image, like image/png or image/jpeg.
        width: The width of the image in pixels.
        height: The height of the image in pixels.
        model: Optionally specify the model used to generate the image.
        prompt: Optionally specify the prompt used to generate the image.
    """

    mime_type: str = field(kw_only=True)
    width: int = field(kw_only=True)
    height: int = field(kw_only=True)
    model: Optional[str] = field(default=None, kw_only=True)
    prompt: Optional[str] = field(default=None, kw_only=True)

    @property
    def base64(self) -> str:
        return base64.b64encode(self.value).decode("utf-8")

    def to_text(self) -> str:
        return f"Image, dimensions: {self.width}x{self.height}, type: {self.mime_type}, size: {len(self.value)} bytes"

    def to_dict(self) -> dict:
        from griptape.schemas import ImageArtifactSchema

        return dict(ImageArtifactSchema().dump(self))
