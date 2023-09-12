from typing import Optional
from attr import field, define
from griptape.artifacts import BaseArtifact


@define
class ListArtifact(BaseArtifact):
    value: list[BaseArtifact] = field(factory=list)

    @value.validator
    def validate_value(self, _, value: list[BaseArtifact]) -> None:
        if len(value) > 0:
            first_type = type(value[0])

            if not all(isinstance(v, first_type) for v in value):
                raise ValueError(f"list elements in 'value' are not the same type")

    def to_text(self) -> str:
        return "\n\n".join([str(v.value) for v in self.value])

    def to_dict(self) -> dict:
        from griptape.schemas import ListArtifactSchema

        return dict(ListArtifactSchema().dump(self))

    def __add__(self, other: BaseArtifact) -> BaseArtifact:
        return ListArtifact(self.value + other.value)

    def elements_type(self) -> Optional[type]:
        if self.value:
            return type(self.value[0])
        else:
            return None

    def is_type(self, target_type: type) -> bool:
        return self.elements_type() == target_type
