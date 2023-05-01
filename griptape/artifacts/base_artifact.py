from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from attr import define, field, Factory


@define
class BaseArtifact(ABC):
    value: Optional[any] = field()
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    @classmethod
    def from_dict(cls, value: dict) -> BaseArtifact:
        from griptape.schemas import TextArtifactSchema, ErrorArtifactSchema

        if value["type"] == "TextArtifact":
            return TextArtifactSchema().load(value)
        elif value["type"] == "ErrorArtifact":
            return ErrorArtifactSchema().load(value)
        else:
            raise ValueError("Unsupported artifact type")

    @abstractmethod
    def __str__(self):
        ...
