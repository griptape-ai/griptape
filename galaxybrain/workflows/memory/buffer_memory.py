from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define, field
from galaxybrain.workflows.memory import Memory

if TYPE_CHECKING:
    from galaxybrain.workflows import Step


@define
class BufferMemory(Memory):
    buffer_size: int = field(default=1, kw_only=True)

    def after_run(self, step: Step) -> None:
        super().after_run(step)

        while len(self.steps) > self.buffer_size:
            self.steps.pop(0)
