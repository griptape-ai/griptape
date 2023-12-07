from __future__ import annotations
from abc import ABC
from attrs import define, field
from typing import Optional, TYPE_CHECKING
from .base_task_event import BaseTaskEvent


if TYPE_CHECKING:
    from griptape.tasks import ActionSubtask


@define
class BaseActionSubtaskEvent(BaseTaskEvent, ABC):
    subtask_parent_task_id: str | None = field(kw_only=True)
    subtask_thought: str | None = field(kw_only=True)
    subtask_action_name: str | None = field(kw_only=True)
    subtask_action_path: str | None = field(kw_only=True)
    subtask_action_input: dict | None = field(kw_only=True)

    @classmethod
    def from_task(cls, task: ActionSubtask) -> BaseActionSubtaskEvent:
        return cls(
            task_id=task.id,
            task_parent_ids=task.parent_ids,
            task_child_ids=task.child_ids,
            task_input=task.input,
            task_output=task.output,
            subtask_parent_task_id=task.parent_task_id,
            subtask_thought=task.thought,
            subtask_action_name=task.action_name,
            subtask_action_path=task.action_path,
            subtask_action_input=task.action_input,
        )
