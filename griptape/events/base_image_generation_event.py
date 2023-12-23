from __future__ import annotations
from attrs import define
from abc import ABC
from .base_event import BaseEvent


@define
class BaseImageGenerationEvent(BaseEvent, ABC):
    ...
