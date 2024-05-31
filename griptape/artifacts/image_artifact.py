from __future__ import annotations

from attrs import define, field

from griptape.artifacts import MediaArtifact


@define
class ImageArtifact(MediaArtifact):
    """ImageArtifact is a type of MediaArtifact representing an image.

    Attributes:
        value: Raw bytes representing media data.
        media_type: The type of media, defaults to "image".
        format: The format of the media, like png, jpeg, or gif.
        name: Artifact name, generated using creation time and a random string.
        model: Optionally specify the model used to generate the media.
        prompt: Optionally specify the prompt used to generate the media.
    """

    media_type: str = "image"
    width: int = field(kw_only=True, metadata={"serializable": True})
    height: int = field(kw_only=True, metadata={"serializable": True})
