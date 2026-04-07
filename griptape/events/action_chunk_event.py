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

    def __str__(self) -> str:
        parts = []

        if self.name:
            parts.append(self.name)
            if self.path:
                parts.append(f".{self.path}")
                if self.tag:
                    parts.append(f" ({self.tag})")

        if self.partial_input:
            if parts:
                parts.append(f"\n{self.partial_input}")
            else:
                parts.append(self.partial_input)

        return "".join(parts)
