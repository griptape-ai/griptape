from __future__ import annotations
from typing import TYPE_CHECKING
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.artifacts.info_artifact import InfoArtifact
from griptape.engines import PromptSummaryEngine
from griptape.tasks import BaseTextInputTask

if TYPE_CHECKING:
    from griptape.engines import BaseSummaryEngine


@define
class TextSummaryTask(BaseTextInputTask):
    summary_engine: BaseSummaryEngine = field(kw_only=True, default=Factory(lambda: PromptSummaryEngine()))

    def run(self) -> TextArtifact | InfoArtifact:
        if self.input_artifact_namespace:
            return self.task_memory.summarize_namespace(self.input_artifact_namespace)
        else:
            return TextArtifact(self.summary_engine.summarize_text(self.input.to_text(), rulesets=self.all_rulesets))
