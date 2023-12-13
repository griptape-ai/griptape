from __future__ import annotations
from attrs import define, field
from abc import ABC
from typing import Optional, TYPE_CHECKING
from griptape.artifacts import BaseArtifact
from .base_event import BaseEvent

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define
class BaseTaskEvent(BaseEvent, ABC):
    task_id: str = field(kw_only=True)
    task_parent_ids: list[str] = field(kw_only=True)
    task_child_ids: list[str] = field(kw_only=True)

    task_input: BaseArtifact = field(kw_only=True)
    task_output: BaseArtifact | None = field(kw_only=True)

    @classmethod
    def from_task(cls, task: BaseTask) -> BaseTaskEvent:
        return cls(
            task_id=task.id,
            task_parent_ids=task.parent_ids,
            task_child_ids=task.child_ids,
            task_input=task.input,
            task_output=task.output,
        )
