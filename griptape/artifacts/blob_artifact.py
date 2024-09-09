from __future__ import annotations

from typing import Any

from attrs import define, field

from griptape.artifacts import BaseArtifact


@define
class BlobArtifact(BaseArtifact):
    """Stores arbitrary binary data.

    Attributes:
        value: The binary data.
        encoding: The encoding to use when converting the binary data to text.
        encoding_error_handler: The error handler to use when converting the binary data to text.
    """

    value: bytes = field(converter=lambda value: BlobArtifact.value_to_bytes(value), metadata={"serializable": True})
    encoding: str = field(default="utf-8", kw_only=True)
    encoding_error_handler: str = field(default="strict", kw_only=True)

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
