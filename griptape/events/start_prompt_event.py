from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define
from attrs import field
from griptape.events.base_prompt_event import BasePromptEvent

if TYPE_CHECKING:
    from griptape.common import MessageStack


@define
class StartPromptEvent(BasePromptEvent):
    message_stack: MessageStack = field(kw_only=True, metadata={"serializable": True})
