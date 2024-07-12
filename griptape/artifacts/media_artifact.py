from __future__ import annotations

import base64
import random
import string
import time
from typing import Optional

from attrs import define, field

from griptape.artifacts import BlobArtifact


@define
class MediaArtifact(BlobArtifact):
    """MediaArtifact is a type of BlobArtifact that represents media (image, audio, video, etc.) and can be extended to support a specific media type.

    Attributes:
        value: Raw bytes representing media data.
        media_type: The type of media, like image, audio, or video.
        format: The format of the media, like png, wav, or mp4.
        name: Artifact name, generated using creation time and a random string.
        model: Optionally specify the model used to generate the media.
        prompt: Optionally specify the prompt used to generate the media.
    """

    media_type: str = field(default="media", kw_only=True, metadata={"serializable": True})
    format: str = field(kw_only=True, metadata={"serializable": True})
    model: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    prompt: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})

    def __attrs_post_init__(self) -> None:
        # Generating the name string requires attributes set by child classes.
        # This waits until all attributes are available before generating a name.
        if self.name == self.id:
            self.name = self.make_name()

    @property
    def mime_type(self) -> str:
        return f"{self.media_type}/{self.format}"

    @property
    def base64(self) -> str:
        return base64.b64encode(self.value).decode("utf-8")

    def to_text(self) -> str:
        return f"Media, type: {self.mime_type}, size: {len(self.value)} bytes"

    def make_name(self) -> str:
        entropy = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        fmt_time = time.strftime("%y%m%d%H%M%S", time.localtime())

        return f"{self.media_type}_artifact_{fmt_time}_{entropy}.{self.format}"
