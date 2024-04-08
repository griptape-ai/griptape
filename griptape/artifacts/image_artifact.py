from __future__ import annotations

import base64

from attr import define, field, Factory

from griptape.artifacts import BaseMediaArtifact


@define
class ImageArtifact(BaseMediaArtifact):
    """ImageArtifact is a type of BaseMediaArtifact that represents an image.

    Attributes:
        value: Raw bytes representing the image.
        name: Artifact name, generated using creation time and a random string.
        format: The format of the image, like png or jpeg.
        mime_type: The mime type of the image, like image/png or image/jpeg.
        width: The width of the image in pixels.
        height: The height of the image in pixels.
        model: Optionally specify the model used to generate the image.
        prompt: Optionally specify the prompt used to generate the image.
    """

    artifact_type: str = "image"
    width: int = field(kw_only=True, metadata={"serializable": True})
    height: int = field(kw_only=True, metadata={"serializable": True})

    @property
    def base64(self) -> str:
        return base64.b64encode(self.value).decode("utf-8")
