from __future__ import annotations

from attr import define, field

from .base_image_generation_event import BaseImageGenerationEvent


@define
class StartImageGenerationEvent(BaseImageGenerationEvent):
    prompts: list[str] = field(kw_only=True)
    negative_prompts: list[str] | None = field(default=None, kw_only=True)

    def to_dict(self) -> dict:
        from griptape.schemas import StartImageGenerationEventSchema

        return dict(StartImageGenerationEventSchema().dump(self))
