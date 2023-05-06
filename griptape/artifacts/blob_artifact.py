import json
import os.path
from typing import Optional
from attr import field, define
from griptape.artifacts import BaseArtifact


@define(frozen=True)
class BlobArtifact(BaseArtifact):
    name: str = field()
    path: Optional[str] = field(default=None, kw_only=True)
    value: bytes = field(kw_only=True)

    @path.validator
    def validate_tools(self, _, path: Optional[str]) -> None:
        if path and path.startswith("/"):
            raise ValueError("path can't be absolute")

    @property
    def full_path(self) -> str:
        return os.path.join(self.path, self.name) if self.path else self.name

    def to_text(self) -> str:
        return self.full_path

    def __str__(self):
        from griptape.schemas import BlobArtifactSchema

        return json.dumps(BlobArtifactSchema().dump(self))
