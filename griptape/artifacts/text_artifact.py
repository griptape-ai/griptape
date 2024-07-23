from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.artifacts import BaseTextArtifact

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact


@define
class TextArtifact(BaseTextArtifact):
    value: str = field(converter=str, metadata={"serializable": True})

    def __add__(self, other: BaseArtifact) -> TextArtifact:
        return TextArtifact(self.value + other.value)

    def __bool__(self) -> bool:
        return bool(self.value.strip())
