from __future__ import annotations

from attrs import define

from .base_actions_subtask_event import BaseActionsSubtaskEvent


@define
class FinishActionsSubtaskEvent(BaseActionsSubtaskEvent): ...
