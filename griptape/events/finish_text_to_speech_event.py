from __future__ import annotations

from attrs import define

from .base_text_to_speech_event import BaseTextToSpeechEvent


@define
class FinishTextToSpeechEvent(BaseTextToSpeechEvent): ...
