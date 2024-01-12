from __future__ import annotations
from attr import define, field
from griptape.artifacts import BaseArtifact


@define
class ErrorArtifact(BaseArtifact):
    value: str = field(converter=str, metadata={"serializable": True})

    def __add__(self, other: BaseArtifact) -> ErrorArtifact:
        return ErrorArtifact(self.value + other.value)
