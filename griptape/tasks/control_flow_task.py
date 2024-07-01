from __future__ import annotations
from typing import Callable
from attrs import define, field

from griptape.artifacts import BaseArtifact, ErrorArtifact, TaskArtifact, ListArtifact
from griptape.tasks import BaseTask
from griptape.tasks import BaseControlFlowTask


@define
class ControlFlowTask(BaseControlFlowTask):
    control_flow_fn: Callable[[list[BaseTask] | BaseTask], list[BaseTask | str] | BaseTask | str] = field(
        metadata={"serializable": False}
    )

    @property
    def input(self) -> BaseArtifact:
        if len(self.parents) == 1:
            return TaskArtifact(self.parents[0])
        return ListArtifact([TaskArtifact(parent) for parent in self.parents])

    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nInput: {self.input.to_text()}")

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nOutput: {self.output.to_text()}")

    def run(self) -> BaseArtifact:
        tasks = self.control_flow_fn(
            [artifact.value for artifact in self.input.value]
            if isinstance(self.input, ListArtifact)
            else self.input.value
        )
        if tasks is None or tasks == []:
            self.output = ErrorArtifact(f"ControlFlowTask {self.id} did not return any tasks")
            return self.output

        if not isinstance(tasks, list):
            tasks = [tasks]

        tasks = [self.structure.find_task(task) if isinstance(task, str) else task for task in tasks]

        for task in tasks:
            self.output = TaskArtifact(task)
            self._cancel_children_rec(self, task)
        return self.output
