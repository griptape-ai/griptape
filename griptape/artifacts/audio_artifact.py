from __future__ import annotations

import random
import string
import time

from attrs import define, field

from griptape.artifacts import BlobArtifact


@define
class AudioArtifact(BlobArtifact):
    """Stores audio data.

    Attributes:
        format: The audio format, e.g. "wav" or "mp3".
    """

    format: str = field(kw_only=True, metadata={"serializable": True})

    def __attrs_post_init__(self) -> None:
        # Generating the name string requires attributes set by child classes.
        # This waits until all attributes are available before generating a name.
        if self.name == self.id:
            self.name = self.make_name()

    @property
    def mime_type(self) -> str:
        return f"audio/{self.format}"

    def to_bytes(self) -> bytes:
        return self.value

    def to_text(self) -> str:
        return f"Audio, format: {self.format}, size: {len(self.value)} bytes"

    def make_name(self) -> str:
        entropy = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        fmt_time = time.strftime("%y%m%d%H%M%S", time.localtime())

        return f"audio_artifact_{fmt_time}_{entropy}.{self.format}"
