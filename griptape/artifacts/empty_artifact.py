from __future__ import annotations

from attrs import define, field

from griptape.artifacts import BaseArtifact


@define
class EmptyArtifact(BaseArtifact):
    """An Artifact with no value. Useful for returning an Artifact with no value.

    Attributes:
        value: The value of the Artifact.
    """

    value: None = field(init=False, default=None)

    def to_text(self) -> str:
        return str(self.value)
