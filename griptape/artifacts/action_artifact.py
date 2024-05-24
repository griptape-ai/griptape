from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional
from collections.abc import Sequence

from attrs import define, field

from griptape.artifacts import BaseArtifact, ActionChunkArtifact
from griptape.mixins import SerializableMixin

if TYPE_CHECKING:
    from griptape.artifacts import BaseChunkArtifact
    from griptape.tools import BaseTool


@define()
class ActionArtifact(BaseArtifact, SerializableMixin):
    """Represents an instance of an LLM taking an action to use a Tool.

    Attributes:
        tag: The tag (unique identifier) of the action.
        name: The name (Tool name) of the action.
        path: The path (Tool activity name) of the action.
        input: The input (Tool params) of the action.
        tool: The tool used in the action.
        output: The output of the action execution.
    """

    @define(kw_only=True)
    class Action(SerializableMixin):
        tag: str = field()
        name: str = field()
        path: Optional[str] = field(default=None)
        input: dict = field(default={})
        tool: Optional[BaseTool] = field(default=None)
        output: Optional[BaseArtifact] = field(default=None)

        def __str__(self) -> str:
            value = f"{self.name} {self.path} {self.input}"
            if self.output:
                value += f" {self.output}"

            return value

        def to_dict(self) -> dict:
            return {
                "tag": self.tag,
                "name": self.name,
                "path": self.path,
                "input": self.input,
                **({"output": self.output.to_dict()} if self.output else {}),
            }

    value: Action = field(metadata={"serializable": True})

    def __add__(self, other: BaseArtifact) -> ActionArtifact:
        raise NotImplementedError

    @classmethod
    def from_chunks(cls, chunks: Sequence[BaseChunkArtifact]) -> ActionArtifact:
        tag = ""
        name = ""
        path = ""
        partial_input = ""

        for chunk in chunks:
            if isinstance(chunk, ActionChunkArtifact):
                tag += chunk.value.tag or ""
                name += chunk.value.name or ""
                path += chunk.value.path or ""
                partial_input += chunk.value.input or ""

        try:
            input = json.loads(partial_input)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON input: {partial_input}, {e}")

        result = ActionArtifact.Action(tag=tag, name=name, path=path, input=input)

        return cls(result)
