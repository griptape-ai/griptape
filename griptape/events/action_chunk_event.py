from typing import Optional

from attr import field
from attrs import define

from griptape.events.base_chunk_event import BaseChunkEvent


@define
class ActionChunkEvent(BaseChunkEvent):
    tag: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    name: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    path: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    partial_input: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
