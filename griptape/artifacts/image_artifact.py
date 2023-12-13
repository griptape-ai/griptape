from __future__ import annotations

import string
import time
import random
from typing import Optional
from attr import define, field, Factory
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
    model: str | None = field(default=None, kw_only=True)
    prompt: str | None = field(default=None, kw_only=True)
    name: str = field(default=Factory(lambda self: self.make_name(), takes_self=True), kw_only=True)

    def make_name(self) -> str:
        entropy = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        fmt_time = time.strftime("%y%m%d%H%M%S", time.localtime())
        extension = self.mime_type.split("/")[1].split("+")[0]

        return f"image_artifact_{fmt_time}_{entropy}.{extension}"

    @property
    def base64(self) -> str:
        return base64.b64encode(self.value).decode("utf-8")

    def to_text(self) -> str:
        return f"Image, dimensions: {self.width}x{self.height}, type: {self.mime_type}, size: {len(self.value)} bytes"

    def to_dict(self) -> dict:
        from griptape.schemas import ImageArtifactSchema

        return dict(ImageArtifactSchema().dump(self))
