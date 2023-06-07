from abc import ABC, abstractmethod
from griptape.artifacts import BaseArtifact


class BaseLoader(ABC):
    @abstractmethod
    def load(self, *args, **kwargs) -> list[BaseArtifact]:
        ...

    @abstractmethod
    def load_collection(self, *args, **kwargs) -> dict[str, list[BaseArtifact]]:
        ...
