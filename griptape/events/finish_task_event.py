from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define, field
from griptape.events.base_event import BaseEvent

if TYPE_CHECKING:
    from griptape.tasks.base_task import BaseTask


@define
class FinishTaskEvent(BaseEvent):
    task: BaseTask = field(kw_only=True)

    def to_dict(self) -> dict:
        from griptape.schemas import FinishTaskEventSchema

        return dict(FinishTaskEventSchema().dump(self))
