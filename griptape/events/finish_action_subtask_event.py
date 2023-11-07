from __future__ import annotations
from attrs import define
from .base_action_subtask_event import BaseActionSubtaskEvent


@define
class FinishActionSubtaskEvent(BaseActionSubtaskEvent):
    def to_dict(self) -> dict:
        from griptape.schemas import FinishApiRequestSubtaskEventSchema

        return dict(FinishApiRequestSubtaskEventSchema().dump(self))
