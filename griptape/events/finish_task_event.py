from __future__ import annotations
from attrs import define
from .base_task_event import BaseTaskEvent


@define
class FinishTaskEvent(BaseTaskEvent):
    def to_dict(self) -> dict:
        from griptape.schemas import FinishTaskEventSchema

        return dict(FinishTaskEventSchema().dump(self))
