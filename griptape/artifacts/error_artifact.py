from attr import define, field
from griptape.artifacts import BaseArtifact


@define(frozen=True)
class ErrorArtifact(BaseArtifact):
    value: str = field()

    def to_text(self) -> str:
        return self.value

    def to_dict(self) -> dict:
        from griptape.schemas import ErrorArtifactSchema

        return dict(ErrorArtifactSchema().dump(self))
