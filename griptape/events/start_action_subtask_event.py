from __future__ import annotations
from attrs import define
from .base_action_subtask_event import BaseActionSubtaskEvent


@define
class StartActionSubtaskEvent(BaseActionSubtaskEvent):
    ...
