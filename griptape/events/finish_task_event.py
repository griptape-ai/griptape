from __future__ import annotations

from attrs import define

from .base_task_event import BaseTaskEvent


@define
class FinishTaskEvent(BaseTaskEvent): ...
