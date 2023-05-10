from __future__ import annotations
import json
from abc import ABC, abstractmethod
from typing import Union
from attr import define, field, Factory
from marshmallow import class_registry
from marshmallow.exceptions import RegistryError


@define
class BaseArtifact(ABC):
    value: Union[str, bytes] = field()
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    @classmethod
    def from_dict(cls, artifact_dict: dict) -> BaseArtifact:
        from griptape.schemas import (
            TextArtifactSchema, InfoArtifactSchema, ErrorArtifactSchema, BlobArtifactSchema, ListArtifactSchema
        )

        class_registry.register("TextArtifact", TextArtifactSchema)
        class_registry.register("InfoArtifact", InfoArtifactSchema)
        class_registry.register("ErrorArtifact", ErrorArtifactSchema)
        class_registry.register("BlobArtifact", BlobArtifactSchema)
        class_registry.register("ListArtifact", ListArtifactSchema)

        try:
            return class_registry.get_class(artifact_dict["type"])().load(artifact_dict)
        except RegistryError:
            raise ValueError("Unsupported artifact type")

    def __str__(self):
        return json.dumps(self.to_dict())

    @abstractmethod
    def to_text(self) -> str:
        ...

    @abstractmethod
    def to_dict(self) -> dict:
        ...
