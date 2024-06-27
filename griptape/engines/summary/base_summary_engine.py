from abc import ABC, abstractmethod
from typing import Any, Optional
from attrs import define, field
from griptape.artifacts import TextArtifact, ListArtifact
from griptape.rules import Ruleset


@define
class BaseSummaryEngine(ABC):
    context: dict[str, Any] = field(factory=dict, kw_only=True)

    def summarize_text(self, text: str, *, rulesets: Optional[list[Ruleset]] = None) -> str:
        return self.summarize_artifacts(ListArtifact([TextArtifact(text)]), rulesets=rulesets).value

    @abstractmethod
    def summarize_artifacts(
        self, artifacts: ListArtifact, *, rulesets: Optional[list[Ruleset]] = None
    ) -> TextArtifact: ...
