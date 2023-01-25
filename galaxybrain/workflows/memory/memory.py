from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define, field
from galaxybrain.utils import J2

if TYPE_CHECKING:
    from galaxybrain.workflows import Step


@define
class Memory:
    steps: list[Step] = field(factory=list, init=False)

    def is_empty(self) -> bool:
        return len(self.steps) == 0

    def before_run(self, step: Step) -> None:
        self.steps.append(step)

    def after_run(self, step: Step) -> None:
        pass

    def to_prompt_string(self):
        return J2("memory.j2").render(
            steps=self.steps
        )

    def to_conversation_string(self):
        return J2("conversation.j2").render(
            steps=self.steps
        )
