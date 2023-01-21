from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import define, field
from galaxybrain.drivers import Driver
from galaxybrain.summarizers.summarizer import Summarizer
from galaxybrain.prompts import Prompt


if TYPE_CHECKING:
    from galaxybrain.workflows import Workflow, Step


@define
class DriverSummarizer(Summarizer):
    driver: Optional[Driver] = field(default=None, kw_only=True)

    def summarize(self, workflow: Workflow, step: Step) -> str:
        if self.driver is None:
            return workflow.to_string()
        else:
            if workflow.memory.summary is None:
                prompt_text = Prompt.summarize(workflow.to_string())
            else:
                prompt_text = Prompt.summarize_summary_and_step(workflow.memory.summary, step)

            return self.driver.run(prompt_text).value
