from abc import ABC, abstractmethod
from attr import define
from griptape.artifacts import TextArtifact, BaseArtifact

@define
class BaseSummaryEngine(ABC):
    def summarize_text(self, text: str, length: int = None, target_audience: str = None, format: str = None) -> str:
        return self.summarize_artifacts([TextArtifact(text)], length, target_audience, format).value

    @abstractmethod
    def summarize_artifacts(self, artifacts: list[BaseArtifact], length: int = None, target_audience: str = None, format: str = None) -> TextArtifact:
        ...
