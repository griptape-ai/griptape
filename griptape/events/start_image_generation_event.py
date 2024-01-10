from __future__ import annotations

from attr import define, field

from .base_image_generation_event import BaseImageGenerationEvent


@define
class StartImageGenerationEvent(BaseImageGenerationEvent):
    prompts: list[str] = field(kw_only=True, metadata={"serialize": True})
    negative_prompts: list[str] | None = field(default=None, kw_only=True, metadata={"serialize": True})
