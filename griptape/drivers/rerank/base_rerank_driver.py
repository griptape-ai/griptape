from abc import ABC, abstractmethod
from attrs import define
from griptape.artifacts import TextArtifact


@define(kw_only=True)
class BaseRerankDriver(ABC):
    @abstractmethod
    def run(self, query: str, artifacts: list[TextArtifact]) -> list[TextArtifact]: ...
