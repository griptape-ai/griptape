from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.engines import PromptSummaryEngine
from griptape.tasks import BaseTextInputTask

if TYPE_CHECKING:
    from griptape.engines import BaseSummaryEngine


@define
class TextSummaryTask(BaseTextInputTask):
    _summary_engine: Optional[BaseSummaryEngine] = field(default=None, alias="summary_engine")

    @property
    def summary_engine(self) -> Optional[BaseSummaryEngine]:
        if self._summary_engine is None:
            if self.structure is not None:
                self._summary_engine = PromptSummaryEngine(prompt_driver=self.structure.config.prompt_driver)
            else:
                raise ValueError("Summary Engine is not set.")
        return self._summary_engine

    @summary_engine.setter
    def summary_engine(self, value: BaseSummaryEngine) -> None:
        self._summary_engine = value

    def run(self) -> TextArtifact:
        return TextArtifact(self.summary_engine.summarize_text(self.input.to_text(), rulesets=self.all_rulesets))
