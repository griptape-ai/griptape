from typing import Optional
from attr import field, define
from griptape.artifacts import BaseArtifact


@define
class ListArtifact(BaseArtifact):
    value: list[BaseArtifact] = field(factory=list)
    item_separator: str = field(default="\n\n", kw_only=True)

    @value.validator
    def validate_value(self, _, value: list[BaseArtifact]) -> None:
        if len(value) > 0:
            first_type = type(value[0])

            if not all(isinstance(v, first_type) for v in value):
                raise ValueError(f"list elements in 'value' are not the same type")

    @property
    def child_type(self) -> Optional[type]:
        if self.value:
            return type(self.value[0])
        else:
            return None

    def __bool__(self) -> bool:
        return len(self) > 0

    def to_text(self) -> str:
        return self.item_separator.join([v.to_text() for v in self.value])

    def to_dict(self) -> dict:
        from griptape.schemas import ListArtifactSchema

        return dict(ListArtifactSchema().dump(self))

    def __add__(self, other: BaseArtifact) -> BaseArtifact:
        return ListArtifact(self.value + other.value)

    def is_type(self, target_type: type) -> bool:
        if self.value:
            return isinstance(self.value[0], target_type)
        else:
            return False

    def has_items(self) -> bool:
        return len(self) > 0
