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
    summary_step_offset: int = field(default=1, kw_only=True)
    summarizer: Optional[Summarizer] = field(default=None, kw_only=True)

    def unsummarized_steps(self) -> list[Step]:
        return [step[0] for step in self.steps if not step[1]]

    def steps_to_summarize(self) -> list[Step]:
        steps = self.unsummarized_steps()

        return steps[:max(0, len(steps) - self.summary_step_offset)]

    def is_empty(self) -> bool:
        return len(self.steps) == 0

    def add_step(self, workflow: Workflow, step: Step) -> None:
        self.steps.append((step, False))

        if self.summarizer is not None:
            steps = self.steps_to_summarize()
            self.summary = self.summarizer.summarize(workflow, steps)

            [self.__summarize_step(step) for step in steps]

    def __summarize_step(self, step: Step) -> None:
        index = next(i for i, s in enumerate(self.steps) if s[0] == step)

        self.steps[index] = (step, True)
