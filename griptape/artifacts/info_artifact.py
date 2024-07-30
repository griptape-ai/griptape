from __future__ import annotations

from attrs import define, field

from griptape.artifacts import BaseArtifact


@define
class InfoArtifact(BaseArtifact):
    value: str = field(converter=str, metadata={"serializable": True})

    def __add__(self, other: BaseArtifact) -> InfoArtifact:
        return InfoArtifact(self.value + other.value)
