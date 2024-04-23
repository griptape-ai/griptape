from __future__ import annotations
from attrs import define
from abc import ABC

from griptape.events.base_media_generation_event import BaseMediaGenerationEvent


@define
class BaseAudioGenerationEvent(BaseMediaGenerationEvent, ABC):
    ...
