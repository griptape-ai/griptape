from __future__ import annotations

from typing import Optional

from attrs import define, field

from griptape.events.base_prompt_event import BasePromptEvent


@define
class FinishPromptEvent(BasePromptEvent):
    result: str = field(kw_only=True, metadata={"serializable": True})
    input_token_count: Optional[float] = field(kw_only=True, metadata={"serializable": True})
    output_token_count: Optional[float] = field(kw_only=True, metadata={"serializable": True})
