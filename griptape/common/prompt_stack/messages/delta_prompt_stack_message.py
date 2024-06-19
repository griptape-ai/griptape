from __future__ import annotations
from typing import Optional

from attrs import define, field

from griptape.common.prompt_stack.contents.text_delta_prompt_stack_content import TextDeltaPromptStackContent


from .base_prompt_stack_message import BasePromptStackMessage


@define
class DeltaPromptStackMessage(BasePromptStackMessage):
    role: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": True})
    content: Optional[TextDeltaPromptStackContent] = field(kw_only=True, default=None, metadata={"serializable": True})
