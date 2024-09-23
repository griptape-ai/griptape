from __future__ import annotations

from attrs import define, field

from griptape.artifacts import BlobArtifact


@define
class VideoArtifact(BlobArtifact):
    """Stores video binary data and relevant metadata.

    Attributes:
        value: The video binary data.
        mime_type: The video MIME type.
        resolution: The resolution of the video (e.g., 1920x1080).
        duration: Duration of the video in seconds.
    """

    aspect_ratio: tuple[int, int] = field(default=(16, 9), kw_only=True)

    @property
    def mime_type(self) -> str:
        return "video/mp4"  # Or make this flexible based on the video format

    def get_aspect_ratio(self) -> tuple[int, int]:
        return self.aspect_ratio

    def to_text(self) -> str:
        raise NotImplementedError("VideoArtifact cannot be converted to text.")
