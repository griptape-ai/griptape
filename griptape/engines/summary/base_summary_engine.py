from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from attrs import define

from griptape.artifacts import ListArtifact, TextArtifact

if TYPE_CHECKING:
    from griptape.rules import Ruleset


@define
class BaseSummaryEngine(ABC):
    def summarize_text(self, text: str, *, rulesets: Optional[list[Ruleset]] = None) -> str:
        return self.summarize_artifacts(ListArtifact([TextArtifact(text)]), rulesets=rulesets).value

    @abstractmethod
    def summarize_artifacts(
        self,
        artifacts: ListArtifact,
        *,
        rulesets: Optional[list[Ruleset]] = None,
    ) -> TextArtifact: ...
