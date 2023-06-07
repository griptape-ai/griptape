from abc import ABC, abstractmethod
from attr import define
from griptape.artifacts import BlobArtifact


@define
class BaseBlobToolMemoryDriver(ABC):
    @abstractmethod
    def save(self, namespace: str, blob: BlobArtifact) -> None:
        ...

    @abstractmethod
    def load(self, namespace: str) -> list[BlobArtifact]:
        ...

    @abstractmethod
    def delete(self, namespace: str) -> None:
        ...
