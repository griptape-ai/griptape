from __future__ import annotations
import os.path
from typing import Optional
from attr import field, define
from griptape.artifacts import BaseArtifact


@define(frozen=True)
class BlobArtifact(BaseArtifact):
    value: bytes = field(converter=BaseArtifact.value_to_bytes)
    dir: Optional[str] = field(default=None, kw_only=True)

    def __add__(self, other: BlobArtifact) -> BlobArtifact:
        return BlobArtifact(self.value + other.value, name=self.name)

    @dir.validator
    def validate_dir(self, _, directory: Optional[str]) -> None:
        if directory and directory.startswith("/"):
            raise ValueError("path can't be absolute")

    @property
    def full_path(self) -> str:
        return os.path.join(self.dir, self.name) if self.dir else self.name

    def to_text(self) -> str:
        return self.full_path

    def to_dict(self) -> dict:
        from griptape.schemas import BlobArtifactSchema

        return dict(BlobArtifactSchema().dump(self))
