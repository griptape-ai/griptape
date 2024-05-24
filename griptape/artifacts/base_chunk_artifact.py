from __future__ import annotations
from abc import abstractmethod
from attrs import define
from griptape.artifacts.base_artifact import BaseArtifact


@define
class BaseChunkArtifact(BaseArtifact):
    @abstractmethod
    def __add__(self, other: BaseArtifact) -> BaseChunkArtifact: ...
