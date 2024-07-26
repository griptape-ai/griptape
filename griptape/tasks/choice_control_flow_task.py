from __future__ import annotations

from typing import Callable

from attrs import define, field

from griptape.artifacts import BaseArtifact, ErrorArtifact, ListArtifact, TextArtifact
from griptape.tasks import BaseControlFlowTask, BaseTask


@define
class ChoiceControlFlowTask(BaseControlFlowTask):
    control_flow_fn: Callable[[list[BaseTask] | BaseTask], list[BaseTask | str] | BaseTask | str] = field(
        metadata={"serializable": False}
    )

    @property
    def input(self) -> BaseArtifact:
        if len(self.parents) == 1:
            return self.parents[0].output if self.parents[0].output is not None else TextArtifact("")
        parents = filter(lambda parent: parent.output is not None, self.parents)
        return ListArtifact(
            [
                parent.output
                for parent in parents  # pyright: ignore[reportArgumentType]
            ]
        )

    def run(self) -> BaseArtifact:
        tasks = self.control_flow_fn(
            [artifact.value for artifact in self.input.value]
            if isinstance(self.input, ListArtifact)
            else self.input.value
        )

        if not isinstance(tasks, list):
            tasks = [tasks]

        if tasks is None:
            tasks = []

        tasks = [self._get_task(task) for task in tasks]

        for task in tasks:
            if task.id not in self.child_ids:
                self.output = ErrorArtifact(f"ControlFlowTask {self.id} did not return a valid child task")
                return self.output

            self.output = (
                ListArtifact(
                    [
                        parent.value.output
                        for parent in filter(lambda parent: parent.value.output is not None, self.input.value)
                    ]
                )
                if isinstance(self.input, ListArtifact)
                else self.input.value.output
            )
            self._cancel_children_rec(self, task)

        return self.output  # pyright: ignore[reportReturnType]
