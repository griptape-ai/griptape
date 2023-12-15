from abc import ABC, abstractmethod
from typing import Optional

from attr import define, field

from griptape.artifacts import ListArtifact, TextArtifact


@define
class BaseGraphDriver(ABC):
    graph_db_hint: str = field(kw_only=True)

    @abstractmethod
    def load_metadata(self, namespace: Optional[str] = None) -> dict:
        ...

    @abstractmethod
    def query(self, query: str, namespace: Optional[str] = None) -> TextArtifact:
        ...

    @abstractmethod
    def load_artifacts(self, namespace: Optional[str] = None) -> ListArtifact:
        ...

    @abstractmethod
    def upsert_text_artifact(self, artifact: TextArtifact, namespace: Optional[str] = None) -> str:
        ...

    @abstractmethod
    def upsert_text_artifacts(self, artifacts: list[TextArtifact], namespace: Optional[str] = None) -> list[str]:
        ...
