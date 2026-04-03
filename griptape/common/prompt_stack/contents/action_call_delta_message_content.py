from __future__ import annotations

from attrs import define, field

from griptape.common import BaseDeltaMessageContent


@define
class ActionCallDeltaMessageContent(BaseDeltaMessageContent):
    tag: str | None = field(default=None, metadata={"serializable": True})
    name: str | None = field(default=None, metadata={"serializable": True})
    path: str | None = field(default=None, metadata={"serializable": True})
    partial_input: str | None = field(default=None, metadata={"serializable": True})

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
                parts.append(f" {self.partial_input}")
            else:
                parts.append(self.partial_input)

        return "".join(parts)
