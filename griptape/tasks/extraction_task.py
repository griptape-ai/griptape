from attr import define, field
from griptape.artifacts import ListArtifact
from griptape.engines import BaseExtractionEngine
from griptape.tasks import PromptTask


@define
class ExtractionTask(PromptTask):
    extraction_engine: BaseExtractionEngine = field(kw_only=True)
    args: dict = field(kw_only=True)

    def run(self) -> ListArtifact:
        return self.extraction_engine.extract(
            self.input.to_text(), rulesets=self.all_rulesets, prompt_stack=self.prompt_stack, **self.args
        )
