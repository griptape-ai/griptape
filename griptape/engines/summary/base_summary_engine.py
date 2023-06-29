from abc import ABC, abstractmethod
from attr import define
from griptape.artifacts import TextArtifact


@define
class BaseSummaryEngine(ABC):
    def summarize_text(self, text: str) -> str:
        return self.summarize_artifacts([TextArtifact(text)]).value

    @abstractmethod
    def summarize_artifacts(self, artifacts: list[TextArtifact]) -> TextArtifact:
        ...
