from abc import ABC, abstractmethod
from typing import Optional

from attr import define
from griptape.artifacts import TextArtifact


@define
class BaseQueryEngine(ABC):
    @abstractmethod
    def query(self, query: str, context: Optional[str] = None, *args, **kwargs) -> TextArtifact:
        ...
