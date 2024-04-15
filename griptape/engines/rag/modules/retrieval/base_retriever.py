from abc import ABC, abstractmethod
from attr import define
from griptape.artifacts import BaseArtifact


@define
class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str) -> list[BaseArtifact]:
        ...
