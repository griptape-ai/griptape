from __future__ import annotations
from attrs import define
from .base_api_request_subtask_event import BaseApiRequestSubtaskEvent


@define
class StartApiRequestSubtaskEvent(BaseApiRequestSubtaskEvent):
    def to_dict(self) -> dict:
        from griptape.schemas import StartApiRequestSubtaskEventSchema

        return dict(StartApiRequestSubtaskEventSchema().dump(self))
