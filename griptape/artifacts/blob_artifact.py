import json
import os.path
from typing import Optional
from attr import field, define
from griptape.artifacts import BaseArtifact


@define(frozen=True)
class BlobArtifact(BaseArtifact):
    value: bytes = field(kw_only=True)
    name: str = field()
    dir: Optional[str] = field(default=None, kw_only=True)

    @dir.validator
    def validate_tools(self, _, dir: Optional[str]) -> None:
        if dir and dir.startswith("/"):
            raise ValueError("path can't be absolute")

    @property
    def full_path(self) -> str:
        return os.path.join(self.dir, self.name) if self.dir else self.name

    def to_text(self) -> str:
        return self.full_path

    def __str__(self):
        from griptape.schemas import BlobArtifactSchema

        return json.dumps(BlobArtifactSchema().dump(self))
