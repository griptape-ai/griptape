from __future__ import annotations

from typing import Optional

from attrs import define, field

from griptape.artifacts import BaseArtifact


@define
class ErrorArtifact(BaseArtifact):
    value: str = field(converter=str, metadata={"serializable": True})
    exception: Optional[Exception] = field(default=None, kw_only=True, metadata={"serializable": False})

    def __add__(self, other: BaseArtifact) -> ErrorArtifact:
        return ErrorArtifact(self.value + other.value)
