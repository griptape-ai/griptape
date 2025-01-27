from __future__ import annotations

from typing import Generic, TypeVar

from attrs import define, field

from griptape.artifacts import BaseArtifact

T = TypeVar("T")


@define
class GenericArtifact(BaseArtifact, Generic[T]):
    """Serves as an escape hatch for artifacts that don't fit into any other category.

    Attributes:
        value: The value of the Artifact.
    """

    value: T = field(metadata={"serializable": True})

    def to_text(self) -> str:
        return str(self.value)
