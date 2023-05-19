from griptape.artifacts import BaseArtifact
from attr import field, define


@define(frozen=True)
class ListArtifact(BaseArtifact):
    value: list[BaseArtifact] = field(factory=list)

    def to_text(self) -> str:
        if len(self.value) > 0:
            values_texts = [value.to_text() for value in self.value]
            string_value = str.join("\n\n", values_texts)

            return f"Artifact contains multiple values:\n{string_value}"
        else:
            return "This artifact is empty"

    def to_dict(self) -> dict:
        from griptape.schemas import ListArtifactSchema

        return dict(ListArtifactSchema().dump(self))
