from __future__ import annotations

from typing import Optional

from attrs import define, field

from griptape.common import BaseDeltaMessageContent

from .base_message import BaseMessage


@define
class DeltaMessage(BaseMessage):
    role: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": True})
    content: Optional[BaseDeltaMessageContent] = field(kw_only=True, default=None, metadata={"serializable": True})
