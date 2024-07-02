from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Union
from attrs import field

from griptape.artifacts import BooleanArtifact
from griptape.tasks import BaseControlFlowTask

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


class BooleanControlFlowTask(BaseControlFlowTask):
    true_tasks: list[str | BaseTask] = field(factory=list, kw_only=True)
    false_tasks: list[str | BaseTask] = field(factory=list, kw_only=True)
    operator: Union[Literal["and"], Literal["or"], Literal["xor"]] = field(default="and", kw_only=True)
    coerce_inputs_to_bool: bool = field(default=False, kw_only=True)

    def run(self) -> BooleanArtifact:
        if not all(
            choice_task if isinstance(choice_task, str) else choice_task.id in self.child_ids
            for choice_task in [*self.true_tasks, *self.false_tasks]
        ):
            raise ValueError(f"BooleanControlFlowTask {self.id} has invalid true_tasks or false_tasks")

        inputs = [task.output for task in self.parents]

        if self.coerce_inputs_to_bool:
            inputs = [BooleanArtifact(input) for input in inputs]
        else:
            if not all(isinstance(input, BooleanArtifact) for input in inputs):
                raise ValueError(f"BooleanControlFlowTask {self.id} has non-BooleanArtifact inputs")

        if self.operator == "and":
            self.output = BooleanArtifact(all(inputs))
        elif self.operator == "or":
            self.output = BooleanArtifact(any(inputs))
        elif self.operator == "xor":
            self.output = BooleanArtifact(sum([int(input.value) for input in inputs]) == 1)
        else:
            raise ValueError(f"BooleanControlFlowTask {self.id} has invalid operator {self.operator}")

        for task in self.true_tasks if self.output.value else self.false_tasks:
            task = self._get_task(task)
            self._cancel_children_rec(self, task)
        return self.output
