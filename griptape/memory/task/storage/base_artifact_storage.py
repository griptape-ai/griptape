from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from attrs import define

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact, InfoArtifact, ListArtifact, TextArtifact


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
