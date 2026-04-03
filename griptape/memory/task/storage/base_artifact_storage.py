from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from attrs import define

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact, ListArtifact


@define
class BaseArtifactStorage(ABC):
    @abstractmethod
    def store_artifact(self, namespace: str, artifact: BaseArtifact) -> None:
        pass

    @abstractmethod
    def load_artifacts(self, namespace: str) -> ListArtifact:
        pass

    @abstractmethod
    def can_store(self, artifact: BaseArtifact) -> bool:
        pass
