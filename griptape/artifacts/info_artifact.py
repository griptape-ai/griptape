from __future__ import annotations

from attrs import define, field

from griptape.artifacts import BaseArtifact


@define
class InfoArtifact(BaseArtifact):
    """Represents helpful info that can be conveyed to the LLM.

    For example, "No results found" or "Please try again.".

    Attributes:
        value: The info to convey.
    """

    value: str = field(converter=str, metadata={"serializable": True})

    def to_text(self) -> str:
        return self.value
