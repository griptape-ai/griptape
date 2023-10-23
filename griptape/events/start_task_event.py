from __future__ import annotations
from attrs import define
from .base_task_event import BaseTaskEvent


@define
class StartTaskEvent(BaseTaskEvent):
    def to_dict(self) -> dict:
        from griptape.schemas import StartTaskEventSchema

        return dict(StartTaskEventSchema().dump(self))
