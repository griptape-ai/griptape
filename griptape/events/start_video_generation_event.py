from __future__ import annotations

from attrs import define, field

from .base_video_generation_event import BaseVideoGenerationEvent


@define
class StartVideoGenerationEvent(BaseVideoGenerationEvent):
    prompt: str = field(kw_only=True, metadata={"serializable": True})
