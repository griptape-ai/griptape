from __future__ import annotations

from typing import Optional

from attrs import define, field

from griptape.artifacts import BaseArtifact


@define
class ErrorArtifact(BaseArtifact):
    """Represents an error that may want to be conveyed to the LLM.

    Attributes:
        value: The error message.
        exception: The exception that caused the error. Defaults to None.
    """

    value: str = field(converter=str, metadata={"serializable": True})
    exception: Optional[Exception] = field(default=None, kw_only=True, metadata={"serializable": False})

    def to_text(self) -> str:
        return self.value
