from __future__ import annotations
from abc import ABC, abstractmethod
from attr import define
from griptape.artifacts import TextArtifact, BaseArtifact


@define
class BaseExtractionEngine(ABC):
    @abstractmethod
    def extract(
            self,
            artifacts: list[TextArtifact],
            fields: list[str]
    ) -> list[BaseArtifact] | BaseArtifact:
        ...
