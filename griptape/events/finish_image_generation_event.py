from __future__ import annotations

from attrs import define

from .base_image_generation_event import BaseImageGenerationEvent


@define
class FinishImageGenerationEvent(BaseImageGenerationEvent): ...
