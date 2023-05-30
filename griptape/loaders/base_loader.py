from abc import ABC, abstractmethod
from griptape.artifacts import BaseArtifact


class BaseLoader(ABC):
    @abstractmethod
    def load(self, *args, **kwargs) -> list[BaseArtifact]:
        ...
