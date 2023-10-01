from abc import ABC, abstractmethod
from attr import define
from griptape.artifacts import TextArtifact, ListArtifact


@define
class BaseSummaryEngine(ABC):
    def summarize_text(self, text: str) -> str:
        return self.summarize_artifacts(
            ListArtifact(
                [TextArtifact(text)]
            )
        ).value

    @abstractmethod
    def summarize_artifacts(self, artifacts: ListArtifact) -> TextArtifact:
        ...
