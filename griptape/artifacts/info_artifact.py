from attr import define, field
from griptape.artifacts import BaseArtifact


@define(frozen=True)
class InfoArtifact(BaseArtifact):
    value: str = field()

    def to_text(self) -> str:
        return self.value

    def to_dict(self) -> dict:
        from griptape.schemas import InfoArtifactSchema

        return dict(InfoArtifactSchema().dump(self))
