from __future__ import annotations

from attrs import define

from .base_audio_generation_event import BaseAudioGenerationEvent
from .base_image_generation_event import BaseImageGenerationEvent


@define
class FinishAudioGenerationEvent(BaseAudioGenerationEvent):
    ...
