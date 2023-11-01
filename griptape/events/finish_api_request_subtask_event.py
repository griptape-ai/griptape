from __future__ import annotations
from attrs import define
from .base_api_request_subtask_event import BaseApiRequestSubtaskEvent


@define
class FinishApiRequestSubtaskEvent(BaseApiRequestSubtaskEvent):
    def to_dict(self) -> dict:
        from griptape.schemas import FinishApiRequestSubtaskEventSchema

        return dict(FinishApiRequestSubtaskEventSchema().dump(self))
