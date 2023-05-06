from __future__ import annotations
from abc import ABC, abstractmethod
from attr import define, field, Factory


@define
class BaseArtifact(ABC):
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    @classmethod
    def from_dict(cls, artifact_dict: dict) -> BaseArtifact:
        from griptape.schemas import TextArtifactSchema, ErrorArtifactSchema, FileArtifactSchema

        if artifact_dict["type"] == "TextArtifact":
            return TextArtifactSchema().load(artifact_dict)
        elif artifact_dict["type"] == "ErrorArtifact":
            return ErrorArtifactSchema().load(artifact_dict)
        elif artifact_dict["type"] == "FileArtifact":
            return FileArtifactSchema().load(artifact_dict)
        else:
            raise ValueError("Unsupported artifact type")

    @abstractmethod
    def to_text(self) -> str:
        ...

    @abstractmethod
    def __str__(self):
        ...
