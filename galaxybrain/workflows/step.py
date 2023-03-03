from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from attrs import define, field, Factory

if TYPE_CHECKING:
    from galaxybrain.artifacts import StepInput, StepOutput
    from galaxybrain.workflows import Step, Workflow


@define
class Step(ABC):
    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)
    input: Optional[StepInput] = field(default=None, kw_only=True)
    parent_id: Optional[str] = field(default=None, kw_only=True)
    child_id: Optional[str] = field(default=None, kw_only=True)

    output: Optional[StepOutput] = field(default=None, init=False)
    workflow: Optional[Workflow] = field(default=None, init=False)

    @property
    def parent(self) -> Optional[Step]:
        return self.workflow.find_step(self.parent_id) if self.parent_id else None

    @property
    def child(self) -> Optional[Step]:
        return self.workflow.find_step(self.child_id) if self.child_id else None

    def add_child(self, child: Step) -> None:
        self.child_id = child.id
        child.parent_id = self.id

    def add_parent(self, parent: Step) -> None:
        parent.child_id = self.id
        self.parent_id = parent.id

    def is_finished(self) -> bool:
        return self.output is not None

    def before_run(self) -> None:
        self.workflow.memory.before_run(self)

    def after_run(self) -> None:
        if self.child:
            self.child.input = self.output

        self.workflow.memory.after_run(self)

    def execute(self) -> StepOutput:
        self.before_run()

        output = self.run()

        self.after_run()

        return output

    @abstractmethod
    def run(self, **kwargs) -> StepOutput:
        pass
