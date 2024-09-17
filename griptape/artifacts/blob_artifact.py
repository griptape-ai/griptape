from __future__ import annotations

import base64

from attrs import define, field

from griptape.artifacts import BaseArtifact


@define
class BlobArtifact(BaseArtifact):
    """Stores arbitrary binary data.

    Attributes:
        value: The binary data.
    """

    value: bytes = field(
        converter=lambda value: value if isinstance(value, bytes) else str(value).encode(),
        metadata={"serializable": True},
    )

    @property
    def base64(self) -> str:
        return base64.b64encode(self.value).decode(self.encoding)

    @property
    def mime_type(self) -> str:
        return "application/octet-stream"

    def to_bytes(self) -> bytes:
        return self.value

    def to_text(self) -> str:
        return self.value.decode(encoding=self.encoding, errors=self.encoding_error_handler)
