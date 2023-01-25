from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Optional
from attrs import define, field
from galaxybrain.utils import J2
from galaxybrain.workflows.memory import Memory

if TYPE_CHECKING:
    from galaxybrain.summarizers import Summarizer
    from galaxybrain.workflows import Step


@define
class SummaryMemory(Memory):
    offset: int = field(default=1, kw_only=True)
    summarizer: Summarizer = field(kw_only=True)
    summary_index: int = field(default=0, init=False)
    summary: Optional[str] = field(default=None, init=False)

    def unsummarized_steps(self) -> list[Step]:
        return self.steps[self.summary_index:]

    def after_run(self, step: Step) -> None:
        super().after_run(step)

        unsummarized_steps = self.unsummarized_steps()
        steps_to_summarize = unsummarized_steps[:max(0, len(unsummarized_steps) - self.offset)]

        if len(steps_to_summarize) > 0:
            self.summary = self.summarizer.summarize(self, steps_to_summarize)
            self.summary_index = 1 + self.steps.index(steps_to_summarize[-1])

    def to_prompt_string(self):
        return J2("memory.j2").render(
            summary=self.summary,
            steps=self.unsummarized_steps()
        )
