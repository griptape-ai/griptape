from __future__ import annotations

from attrs import define, field

from .base_text_to_speech_event import BaseTextToSpeechEvent


@define
class StartTextToSpeechEvent(BaseTextToSpeechEvent):
    prompts: list[str] = field(kw_only=True, metadata={"serializable": True})
