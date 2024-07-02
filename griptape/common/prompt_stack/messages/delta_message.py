from __future__ import annotations

from typing import Optional

from attrs import define, field

from griptape.common import BaseDeltaPromptStackContent

from .base_message import BaseMessage


@define
class DeltaMessage(BaseMessage):
    role: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": True})
    content: Optional[BaseDeltaPromptStackContent] = field(kw_only=True, default=None, metadata={"serializable": True})
