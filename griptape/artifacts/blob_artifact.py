from __future__ import annotations

from typing import Any

from attrs import define, field

from griptape.artifacts import BaseArtifact


@define
class BlobArtifact(BaseArtifact):
    """Stores arbitrary binary data.

    Attributes:
        value: The binary data.
    """

    value: bytes = field(converter=lambda value: BlobArtifact.value_to_bytes(value), metadata={"serializable": True})

    @property
    def mime_type(self) -> str:
        return "application/octet-stream"

    @classmethod
    def value_to_bytes(cls, value: Any) -> bytes:
        if isinstance(value, bytes):
            return value
        else:
            return str(value).encode()

    def to_bytes(self) -> bytes:
        return self.value

    def to_text(self) -> str:
        return self.value.decode(encoding=self.encoding, errors=self.encoding_error_handler)
