from __future__ import annotations
from abc import ABC
from attrs import define, field
from typing import Optional, TYPE_CHECKING
from .base_task_event import BaseTaskEvent


if TYPE_CHECKING:
    from griptape.tasks import ApiRequestSubtask


@define
class BaseApiRequestSubtaskEvent(BaseTaskEvent, ABC):
    subtask_parent_task_id: Optional[str] = field(kw_only=True)
    subtask_thought: Optional[str] = field(kw_only=True)
    subtask_api_name: Optional[str] = field(kw_only=True)
    subtask_api_path: Optional[str] = field(kw_only=True)
    subtask_api_input: Optional[dict] = field(kw_only=True)

    @classmethod
    def from_task(cls, task: ApiRequestSubtask) -> BaseApiRequestSubtaskEvent:
        return cls(
            task_id=task.id,
            task_parent_ids=task.parent_ids,
            task_child_ids=task.child_ids,
            task_input=task.input,
            task_output=task.output,
            subtask_parent_task_id=task.parent_task_id,
            subtask_thought=task.thought,
            subtask_api_name=task.api_name,
            subtask_api_path=task.api_path,
            subtask_api_input=task.api_input,
        )
