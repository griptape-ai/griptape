from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.engines import PromptSummaryEngine
from griptape.tasks import PromptTask

if TYPE_CHECKING:
    from griptape.engines import BaseSummaryEngine


@define
class TextSummaryTask(PromptTask):
    summary_engine: BaseSummaryEngine = field(kw_only=True, default=Factory(lambda: PromptSummaryEngine()))

    def run(self) -> TextArtifact:
        return TextArtifact(
            self.summary_engine.summarize_text(
                self.input.to_text(), rulesets=self.all_rulesets, prompt_stack=self.prompt_stack
            )
        )
