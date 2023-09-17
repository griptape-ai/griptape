from __future__ import annotations
import os.path
from typing import Optional
from attr import field, define
from griptape.artifacts import BaseArtifact


@define(frozen=True)
class BlobArtifact(BaseArtifact):
    value: bytes = field(converter=BaseArtifact.value_to_bytes)
    dir_name: Optional[str] = field(default=None, kw_only=True)

    def __add__(self, other: BlobArtifact) -> BlobArtifact:
        return BlobArtifact(self.value + other.value, name=self.name)

    @property
    def full_path(self) -> str:
        return os.path.join(self.dir_name, self.name) if self.dir_name else self.name

    def to_text(self) -> str:
        return self.full_path

    def to_dict(self) -> dict:
        from griptape.schemas import BlobArtifactSchema

        return dict(BlobArtifactSchema().dump(self))
