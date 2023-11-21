from __future__ import annotations

import string
import time
import random
from typing import Optional
from attr import define, field, Factory
from griptape.artifacts import BlobArtifact


@define(frozen=True)
class ImageArtifact(BlobArtifact):
    mime_type: str = field(kw_only=True)
    width: int = field(kw_only=True)
    height: int = field(kw_only=True)
    model: Optional[str] = field(default=None, kw_only=True)
    prompt: Optional[str] = field(default=None, kw_only=True)
    name: str = field(default=Factory(lambda self: self.make_name(), takes_self=True), kw_only=True)

    def make_name(self) -> str:
        entropy = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        fmt_time = time.strftime("%y%m%d%H%M%S", time.localtime())
        extension = self.mime_type.split("/")[1].split("+")[0]

        return f"image_artifact_{fmt_time}_{entropy}.{extension}"

    def to_text(self) -> str:
        return f"Image, dimensions: {self.width}x{self.height}, type: {self.mime_type}, size: {len(self.value)} bytes"

    def to_dict(self) -> dict:
        from griptape.schemas import ImageArtifactSchema

        return dict(ImageArtifactSchema().dump(self))
