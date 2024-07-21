from __future__ import annotations

from abc import ABC

from attrs import define, field

from .base_event import BaseEvent


@define
class BasePromptEvent(BaseEvent, ABC):
    model: str = field(kw_only=True, metadata={"serializable": True})
