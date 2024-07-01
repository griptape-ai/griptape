from __future__ import annotations
from typing import Optional

from attrs import define, field

from griptape.common.prompt_stack.contents.text_delta_message_content import TextDeltaMessageContent


from .base_message import BaseMessage


@define
class DeltaMessage(BaseMessage):
    role: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": True})
    content: Optional[TextDeltaMessageContent] = field(kw_only=True, default=None, metadata={"serializable": True})
