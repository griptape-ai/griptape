from __future__ import annotations
from typing import Any
from abc import ABC, abstractmethod
from attrs import define
from griptape.artifacts import BaseArtifact, ListArtifact, TextArtifact, InfoArtifact


@define
class BaseArtifactStorage(ABC):
    @abstractmethod
    def store_artifact(self, namespace: str, artifact: BaseArtifact) -> None: ...

    @abstractmethod
    def load_artifacts(self, namespace: str) -> ListArtifact: ...

    @abstractmethod
    def can_store(self, artifact: BaseArtifact) -> bool: ...

    @abstractmethod
    def summarize(self, namespace: str) -> TextArtifact | InfoArtifact: ...

    @abstractmethod
    def query(self, namespace: str, query: str, metadata: Any = None) -> BaseArtifact: ...
