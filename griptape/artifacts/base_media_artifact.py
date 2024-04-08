from __future__ import annotations

from abc import ABC

import string
import time
import random
from typing import Optional

from attr import define, field
from griptape.artifacts import BlobArtifact
import base64


@define
class BaseMediaArtifact(BlobArtifact, ABC):
    """BaseMediaArtifact is a type of BlobArtifact that represents media (image, audio, video, etc.).

    Attributes:
        value: Raw bytes representing media data.
        name: Artifact name, generated using creation time and a random string.
        mime_type: The mime type of the image, like image/png or audio/wav.
        model: Optionally specify the model used to generate the media.
        prompt: Optionally specify the prompt used to generate the media.
    """

    artifact_type: str = field(default="media", kw_only=True, metadata={"serializable": True})
    format: str = field(kw_only=True, metadata={"serializable": True})
    model: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    prompt: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})

    def __attrs_post_init__(self):
        # Generating the name string requires attributes set by child classes.
        # This waits until all attributes are available before generating a name.
        if self.name == self.id:
            self.name = self.make_name()

    @property
    def mime_type(self) -> str:
        return f"{self.artifact_type}/{self.format}"

    def make_name(self) -> str:
        entropy = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        fmt_time = time.strftime("%y%m%d%H%M%S", time.localtime())

        return f"{self.artifact_type}_artifact_{fmt_time}_{entropy}.{self.format}"

    @property
    def base64(self) -> str:
        return base64.b64encode(self.value).decode("utf-8")

    def to_text(self) -> str:
        return f"Media, type: {self.mime_type}, size: {len(self.value)} bytes"
