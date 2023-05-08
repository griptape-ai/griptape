from __future__ import annotations
import json
from abc import ABC, abstractmethod
from typing import Union
from attr import define, field, Factory


@define
class BaseArtifact(ABC):
    value: Union[str, bytes] = field()
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    @classmethod
    def from_dict(cls, artifact_dict: dict) -> BaseArtifact:
        from griptape.schemas import TextArtifactSchema, ErrorArtifactSchema, BlobArtifactSchema

        if artifact_dict["type"] == "TextArtifact":
            return TextArtifactSchema().load(artifact_dict)
        elif artifact_dict["type"] == "ErrorArtifact":
            return ErrorArtifactSchema().load(artifact_dict)
        elif artifact_dict["type"] == "BlobArtifact":
            return BlobArtifactSchema().load(artifact_dict)
        else:
            raise ValueError("Unsupported artifact type")

    def __str__(self):
        return json.dumps(self.to_dict())

    @abstractmethod
    def to_text(self) -> str:
        ...

    @abstractmethod
    def to_dict(self) -> dict:
        ...
