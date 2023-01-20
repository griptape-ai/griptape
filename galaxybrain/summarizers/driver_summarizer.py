from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define
from galaxybrain.summarizers.summarizer import Summarizer
from galaxybrain.prompts import Prompt


if TYPE_CHECKING:
    from galaxybrain.workflows import Workflow, Step


@define
class DriverSummarizer(Summarizer):
    def summarize(self, workflow: Workflow, step: Step) -> str:
        if workflow.memory.summary is None:
            prompt_text = Prompt.summarize(workflow.to_string())
        else:
            prompt_text = Prompt.summarize_summary_and_step(workflow.memory.summary, step)

        return workflow.driver.run(prompt_text).value
