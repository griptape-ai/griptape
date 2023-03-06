from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define, field
from warpspeed.utils import J2

if TYPE_CHECKING:
    from warpspeed.steps import Step


@define
class Memory:
    steps: list[Step] = field(factory=list, init=False)

    def is_empty(self) -> bool:
        return not self.steps

    def before_run(self, step: Step) -> None:
        self.steps.append(step)

    def after_run(self, step: Step) -> None:
        pass

    def to_prompt_string(self) -> str:
        return J2("prompts/memory.j2").render(
            steps=self.steps
        )
