import json
from attr import define, field
from griptape.artifacts import BaseArtifact


@define(frozen=True)
class ErrorArtifact(BaseArtifact):
    value: str = field()

    def to_text(self) -> str:
        return self.value

    def __str__(self):
        from griptape.schemas import ErrorArtifactSchema

        return json.dumps(ErrorArtifactSchema().dump(self))
