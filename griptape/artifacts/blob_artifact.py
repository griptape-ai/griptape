import json
from attr import field, define
from griptape.artifacts import BaseArtifact


@define(frozen=True)
class BlobArtifact(BaseArtifact):
    name: str = field()
    value: bytes = field(kw_only=True)

    def to_text(self) -> str:
        return self.name

    def __str__(self):
        from griptape.schemas import BlobArtifactSchema

        return json.dumps(BlobArtifactSchema().dump(self))
