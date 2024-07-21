from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from .base_message import BaseMessage

if TYPE_CHECKING:
    from griptape.common import BaseDeltaMessageContent


@define
class DeltaMessage(BaseMessage):
    role: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": True})
    content: Optional[BaseDeltaMessageContent] = field(kw_only=True, default=None, metadata={"serializable": True})
