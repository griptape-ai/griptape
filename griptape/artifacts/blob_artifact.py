from __future__ import annotations

import os.path
from typing import Optional

from attrs import define, field

from griptape.artifacts import BaseArtifact


@define
class BlobArtifact(BaseArtifact):
    value: bytes = field(converter=BaseArtifact.value_to_bytes, metadata={"serializable": True})
    dir_name: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    encoding: str = field(default="utf-8", kw_only=True)
    encoding_error_handler: str = field(default="strict", kw_only=True)

    def __add__(self, other: BaseArtifact) -> BlobArtifact:
        return BlobArtifact(self.value + other.value, name=self.name)

    @property
    def full_path(self) -> str:
        return os.path.join(self.dir_name, self.name) if self.dir_name else self.name

    def to_text(self) -> str:
        return self.value.decode(encoding=self.encoding, errors=self.encoding_error_handler)
