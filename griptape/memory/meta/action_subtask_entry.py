from __future__ import annotations
from typing import TYPE_CHECKING
from attr import field, define
from griptape.memory.meta import BaseMetaEntry

if TYPE_CHECKING:
    from griptape.tasks import ActionSubtask


@define
class ActionSubtaskEntry(BaseMetaEntry):
    thought: str = field(kw_only=True)
    action: str = field(kw_only=True)
    answer: str = field(kw_only=True)

    @classmethod
    def from_action_subtask(cls, action_subtask: ActionSubtask) -> ActionSubtaskEntry:
        return ActionSubtaskEntry(
            thought=action_subtask.thought,
            action=action_subtask.action_to_json(),
            answer=action_subtask.output.to_text()
        )

    def to_dict(self) -> dict:
        return {
            "thought": self.thought,
            "action": self.action,
            "answer": self.answer
        }
