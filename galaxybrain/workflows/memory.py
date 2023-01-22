from __future__ import annotations
from typing import TYPE_CHECKING, Tuple
from typing import Optional
from attrs import define, field
from galaxybrain.summarizers import Summarizer

if TYPE_CHECKING:
    from galaxybrain.workflows import Step, Workflow


@define
class Memory:
    steps: list[Tuple[Step, bool]] = []
    should_summarize: bool = True
    summary: Optional[str] = None
    summarizer: Optional[Summarizer] = field(default=None, kw_only=True)

    def unsummarized_steps(self) -> list[Step]:
        return [step[0] for step in self.steps if not step[1]]

    def is_empty(self) -> bool:
        return len(self.steps) == 0

    def add_step(self, workflow: Workflow, step: Step) -> None:
        self.steps.append((step, False))
        step_index = len(self.steps) - 1

        if self.summarizer is not None:
            self.summary = self.summarizer.summarize(workflow, step)

            self.steps[step_index] = (step, True)
