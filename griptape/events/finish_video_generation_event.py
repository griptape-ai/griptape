from __future__ import annotations

from attrs import define

from .base_video_generation_event import BaseVideoGenerationEvent


@define
class FinishVideoGenerationEvent(BaseVideoGenerationEvent): ...
