from abc import ABC, abstractmethod
from typing import Optional
from attr import define
from griptape.artifacts import TextArtifact, ListArtifact


@define
class BaseQueryEngine(ABC):
    @abstractmethod
    def query(self, *args, **kwargs) -> TextArtifact:
        ...

    @abstractmethod
    def load_artifacts(self, namespace: str) -> ListArtifact:
        ...

    @abstractmethod
    def upsert_text_artifact(self, artifact: TextArtifact, namespace: Optional[str] = None) -> str:
        ...

    @abstractmethod
    def upsert_text_artifacts(self, artifacts: list[TextArtifact], namespace: str) -> None:
        ...
