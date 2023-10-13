from abc import ABC, abstractmethod
from attr import define
from griptape.artifacts import BaseArtifact, ListArtifact


@define
class BaseToolMemoryStorage(ABC):
    @abstractmethod
    def store_artifact(self, namespace: str, artifact: BaseArtifact) -> None:
        ...

    @abstractmethod
    def load_artifacts(self, namespace: str) -> ListArtifact:
        ...

    @abstractmethod
    def can_store(self, artifact: BaseArtifact) -> bool:
        ...
