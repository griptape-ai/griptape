from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define, field
from griptape.events.base_event import BaseEvent

if TYPE_CHECKING:
    from griptape.tasks.base_task import BaseTask


@define
class FinishTaskEvent(BaseEvent):
    task: BaseTask = field(kw_only=True)
