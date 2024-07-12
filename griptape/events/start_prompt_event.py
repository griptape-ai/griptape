from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.events.base_prompt_event import BasePromptEvent

if TYPE_CHECKING:
    from griptape.common import PromptStack


@define
class StartPromptEvent(BasePromptEvent):
    prompt_stack: PromptStack = field(kw_only=True, metadata={"serializable": True})
