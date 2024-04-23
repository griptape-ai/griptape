from __future__ import annotations

from typing import Optional
from attr import define, field

from .base_audio_generation_event import BaseAudioGenerationEvent


@define
class StartAudioGenerationEvent(BaseAudioGenerationEvent):
    prompts: list[str] = field(kw_only=True, metadata={"serializable": True})
    negative_prompts: Optional[list[str]] = field(default=None, kw_only=True, metadata={"serializable": True})
