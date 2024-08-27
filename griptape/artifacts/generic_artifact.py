from __future__ import annotations

from typing import Any

from attrs import define, field

from griptape.artifacts import BaseArtifact


@define
class GenericArtifact(BaseArtifact):
    """Serves as an escape hatch for artifacts that don't fit into any other category.

    Attributes:
        value: The value of the Artifact.
    """

    value: Any = field(metadata={"serializable": True})

    def to_text(self) -> str:
        return str(self.value)
