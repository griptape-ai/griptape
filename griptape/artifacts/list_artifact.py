from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import Attribute, define, field

from griptape.artifacts import BaseArtifact

if TYPE_CHECKING:
    from collections.abc import Sequence


@define
class ListArtifact(BaseArtifact):
    value: Sequence[BaseArtifact] = field(factory=list, metadata={"serializable": True})
    item_separator: str = field(default="\n\n", kw_only=True, metadata={"serializable": True})
    validate_uniform_types: bool = field(default=False, kw_only=True, metadata={"serializable": True})

    @value.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_value(self, _: Attribute, value: list[BaseArtifact]) -> None:
        if self.validate_uniform_types and len(value) > 0:
            first_type = type(value[0])

            if not all(isinstance(v, first_type) for v in value):
                raise ValueError("list elements in 'value' are not the same type")

    @property
    def child_type(self) -> Optional[type]:
        if self.value:
            return type(self.value[0])
        else:
            return None

    def __getitem__(self, key: int) -> BaseArtifact:
        return self.value[key]

    def __bool__(self) -> bool:
        return len(self) > 0

    def to_text(self) -> str:
        return self.item_separator.join([v.to_text() for v in self.value])

    def __add__(self, other: BaseArtifact) -> BaseArtifact:
        return ListArtifact(self.value + other.value)

    def is_type(self, target_type: type) -> bool:
        if self.value:
            return isinstance(self.value[0], target_type)
        else:
            return False

    def has_items(self) -> bool:
        return len(self) > 0
