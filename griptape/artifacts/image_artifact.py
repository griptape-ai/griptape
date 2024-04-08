from __future__ import annotations

from attr import define, field

from griptape.artifacts import MediaArtifact


@define
class ImageArtifact(MediaArtifact):
    """ImageArtifact is a type of MediaArtifact representing an image.

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
