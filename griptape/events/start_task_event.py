from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define, field
from griptape.events.base_event import BaseEvent

if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define
class StartTaskEvent(BaseEvent):
    task: BaseTask = field(kw_only=True)

    def to_dict(self) -> dict:
        from griptape.schemas import StartTaskEventSchema

        return dict(StartTaskEventSchema().dump(self))
