from abc import ABC, abstractmethod
from attr import define
from griptape.artifacts import BaseArtifact


@define(kw_only=True)
class BaseRetriever(ABC):
    @abstractmethod
    def run(self, query: str) -> list[BaseArtifact]:
        ...
