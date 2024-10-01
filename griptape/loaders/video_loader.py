from __future__ import annotations

from io import BytesIO
from typing import Optional, cast

from attrs import define, field

from griptape.artifacts import VideoArtifact
from griptape.loaders import BaseLoader
from griptape.utils import import_optional_dependency


@define
class VideoLoader(BaseLoader):
    """Loads videos into video artifacts.

    Attributes:
        format: If provided, attempts to ensure video artifacts are in this format when loaded.
                For example, when set to 'mp4', loading video.webm will return a VideoArtifact containing the video
                    bytes in MP4 format.
    """

    format: Optional[str] = field(default=None, kw_only=True)

    FORMAT_TO_MIME_TYPE = {
        "mp4": "video/mp4",
        "webm": "video/webm",
        "ogg": "video/ogg",
    }

    def load(self, source: bytes, *args, **kwargs) -> VideoArtifact:
        moviepy = import_optional_dependency("moviepy.editor")
        video = moviepy.VideoFileClip(BytesIO(source))

        # Normalize format only if requested.
        if self.format is not None:
            byte_stream = BytesIO()
            video.write_videofile(byte_stream, codec="libx264", format=self.format)
            video = moviepy.VideoFileClip(byte_stream)
            source = byte_stream.getvalue()
        return VideoArtifact(source, aspect_ratio=(video.size[0], video.size[1]))

    def _get_mime_type(self, video_format: str | None) -> str:
        if video_format is None:
            raise ValueError("video_format is None")

        if video_format.lower() not in self.FORMAT_TO_MIME_TYPE:
            raise ValueError(f"Unsupported video format {video_format}")

        return self.FORMAT_TO_MIME_TYPE[video_format.lower()]

    def load_collection(self, sources: list[bytes], *args, **kwargs) -> dict[str, VideoArtifact]:
        return cast(dict[str, VideoArtifact], super().load_collection(sources, *args, **kwargs))
