from __future__ import annotations
from attrs import define, field
from typing import Optional

from griptape.common import BaseDeltaMessageContent


@define
class ActionCallDeltaMessageContent(BaseDeltaMessageContent):
    tag: Optional[str] = field(default=None, metadata={"serializable": True})
    name: Optional[str] = field(default=None, metadata={"serializable": True})
    path: Optional[str] = field(default=None, metadata={"serializable": True})
    partial_input: Optional[str] = field(default=None, metadata={"serializable": True})

    def __str__(self) -> str:
        output = ""

        if self.name is not None:
            output += f"{self.name}"
            if self.path is not None:
                output += f".{self.path}"
                if self.tag is not None:
                    output += f" ({self.tag})"
        if self.partial_input is not None:
            output += f" {self.partial_input}"

        return output
