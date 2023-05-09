from abc import ABC, abstractmethod
from typing import Optional
from attr import define
from griptape.artifacts import BlobArtifact


@define
class BaseBlobStorageDriver(ABC):
    @abstractmethod
    def save(self, blob: BlobArtifact) -> str:
        ...

    @abstractmethod
    def load(self, key: str) -> Optional[BlobArtifact]:
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        ...
