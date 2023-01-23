from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from galaxybrain.drivers import CompletionDriver
from galaxybrain.summarizers.summarizer import Summarizer
from galaxybrain.prompts import Prompt


if TYPE_CHECKING:
    from galaxybrain.workflows import Workflow, Step


@define
class CompletionDriverSummarizer(Summarizer):
    driver: CompletionDriver = field(kw_only=True)

    def summarize(self, workflow: Workflow, steps: list[Step]) -> Optional[str]:
        if len(steps) > 0:
            return self.driver.run(
                value=Prompt.summarize(workflow.memory.summary, steps)
            ).value
        else:
            return workflow.memory.summary
