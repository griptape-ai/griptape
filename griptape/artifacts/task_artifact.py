from __future__ import annotations
from attrs import define, field
from typing import TYPE_CHECKING
from griptape.artifacts import ControlFlowArtifact

if TYPE_CHECKING:
    from griptape.tasks import BaseTask
    from griptape.artifacts import BaseArtifact


@define
class TaskArtifact(ControlFlowArtifact):
    value: BaseTask = field(metadata={"serializable": True})

    @property
    def task_id(self) -> str:
        return self.value.id

    @property
    def task(self) -> BaseTask:
        return self.value

    def to_text(self) -> str:
        return self.value.id

    def __add__(self, other: BaseArtifact) -> BaseArtifact:
        raise NotImplementedError("TaskArtifact does not support addition")

    def __eq__(self, value: object) -> bool:
        return self.value is value
