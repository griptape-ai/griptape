from __future__ import annotations

import random
import string
import time

from attrs import define, field

from griptape.artifacts import BlobArtifact


@define
class ImageArtifact(BlobArtifact):
    """Stores image data.

    Attributes:
        format: The format of the image data. Used when building the MIME type.
        width: The width of the image.
        height: The height of the image
    """

    format: str = field(kw_only=True, metadata={"serializable": True})
    width: int = field(kw_only=True, metadata={"serializable": True})
    height: int = field(kw_only=True, metadata={"serializable": True})

    def __attrs_post_init__(self) -> None:
        # Generating the name string requires attributes set by child classes.
        # This waits until all attributes are available before generating a name.
        if self.name == self.id:
            self.name = self.make_name()

    @property
    def mime_type(self) -> str:
        return f"image/{self.format}"

    def to_bytes(self) -> bytes:
        return self.value

    def to_text(self) -> str:
        return f"Image, format: {self.format}, size: {len(self.value)} bytes"

    def make_name(self) -> str:
        entropy = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        fmt_time = time.strftime("%y%m%d%H%M%S", time.localtime())

        return f"image_artifact_{fmt_time}_{entropy}.{self.format}"
