from __future__ import annotations

from typing import Optional

from attrs import define, field

from griptape.events.base_chunk_event import BaseChunkEvent


@define
class ActionChunkEvent(BaseChunkEvent):
    partial_input: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    tag: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    name: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    path: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
