from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Optional
from attrs import define

if TYPE_CHECKING:
    from galaxybrain.workflows import Step


@define
class Memory:
    steps: list[Step] = []
    should_summarize: bool = True
    summary: Optional[str] = None

    def is_empty(self) -> bool:
        return len(self.steps) == 0

    def add_step(self, step: Step) -> None:
        self.steps.append(step)

    def to_string(self):
        return "\n".join([step.name() for step in self.steps])
