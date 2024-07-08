from __future__ import annotations
import json
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.artifacts import BaseArtifact
from griptape.mixins import SerializableMixin

if TYPE_CHECKING:
    from griptape.tools import BaseTool


@define(kw_only=True)
class Action(SerializableMixin):
    tag: str = field(metadata={"serializable": True})
    name: str = field(metadata={"serializable": True})
    path: Optional[str] = field(default=None, metadata={"serializable": True})
    input: dict = field(factory=dict, metadata={"serializable": True})
    tool: Optional[BaseTool] = field(default=None)
    output: Optional[BaseArtifact] = field(default=None, metadata={"serializable": True})

    def __str__(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return {"tag": self.tag, "name": self.name, "path": self.path, "input": self.input}

    def to_native_tool_name(self) -> str:
        parts = [self.name]

        if self.path is not None:
            parts.append(self.path)

        return "_".join(parts)

    @classmethod
    def from_native_tool_name(cls, native_tool_name: str) -> tuple[str, Optional[str]]:
        parts = native_tool_name.split("_", 1)

        if len(parts) == 1:
            name, path = parts[0], None
        else:
            name, path = parts

        return name, path
