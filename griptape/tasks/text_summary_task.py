from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.engines import BaseSummaryEngine, PromptSummaryEngine
from griptape.tasks import BaseTextInputTask

@define
class TextSummaryTask(BaseTextInputTask):
    summary_engine: BaseSummaryEngine = field(
        kw_only=True,
        default=Factory(lambda: PromptSummaryEngine())
    )
    length: int = field(default=None, kw_only=True)
    target_audience: str = field(default=None, kw_only=True)
    format: str = field(default=None, kw_only=True)

    def run(self) -> TextArtifact:
        return TextArtifact(
            self.summary_engine.summarize_text(
                self.input.to_text(),
                length=self.length,
                target_audience=self.target_audience,
                format=self.format
            )
        )
