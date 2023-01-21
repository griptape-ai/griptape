from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Optional
from attrs import define, field
from galaxybrain.summarizers import Summarizer

if TYPE_CHECKING:
    from galaxybrain.workflows import Step, Workflow


@define
class Memory:
    steps: list[Step] = []
    should_summarize: bool = True
    summary: Optional[str] = None
    summarizer: Optional[Summarizer] = field(default=None, kw_only=True)

    def is_empty(self) -> bool:
        return len(self.steps) == 0

    def add_step(self, workflow: Workflow, step: Step) -> None:
        self.steps.append(step)

        if self.summarizer is not None:
            self.summary = self.summarizer.summarize(workflow, step)

    def to_string(self):
        return "\n".join([step.name() for step in self.steps])
