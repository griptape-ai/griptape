from __future__ import annotations

from abc import ABC

from attrs import define

from .base_media_generation_event import BaseMediaGenerationEvent


@define
class BaseImageGenerationEvent(BaseMediaGenerationEvent, ABC): ...
