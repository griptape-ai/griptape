from __future__ import annotations

from typing import Any

from attrs import define, field

from griptape.artifacts import BaseArtifact


@define
class GenericArtifact(BaseArtifact):
    value: Any = field(metadata={"serializable": True})

    def __add__(self, other: BaseArtifact) -> BaseArtifact:
        raise NotImplementedError
