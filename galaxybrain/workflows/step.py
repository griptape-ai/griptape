from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from attrs import define, field

if TYPE_CHECKING:

    from galaxybrain.rules import Rule
    from galaxybrain.workflows import Step, StepInput, StepOutput, Memory


@define
class Step(ABC):
    input: StepInput
    output: Optional[StepOutput] = field(default=None, init=False)
    parent: Optional[Step] = field(default=None, kw_only=True)
    child: Optional[Step] = field(default=None, kw_only=True)

    def add_child(self, child: Step) -> None:
        self.child = child
        child.parent = self

    def add_parent(self, parent: Step) -> None:
        parent.child = self
        self.parent = parent

    def name(self) -> str:
        return type(self).__name__

    def is_finished(self):
        return self.output is not None

    @abstractmethod
    def run(self, **kwargs) -> StepOutput:
        pass

    @abstractmethod
    def to_string(self, rules: list[Rule], memory: Memory) -> str:
        pass
