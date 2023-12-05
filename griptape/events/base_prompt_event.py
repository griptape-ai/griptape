from __future__ import annotations
from attrs import define, field
from abc import ABC
from griptape.utils import PromptStack
from .base_event import BaseEvent


@define
class BasePromptEvent(BaseEvent, ABC):
    token_count: int = field(kw_only=True)
    prompt_stack: PromptStack = field(kw_only=True)
    prompt: str = field(kw_only=True)
