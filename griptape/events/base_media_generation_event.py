from __future__ import annotations

from abc import ABC

from attrs import define

from .base_event import BaseEvent


@define
class BaseMediaGenerationEvent(BaseEvent, ABC): ...
