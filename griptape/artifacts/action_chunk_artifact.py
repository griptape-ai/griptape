from __future__ import annotations

from typing import Optional

from attr import define, field

from griptape.artifacts import BaseArtifact, BaseChunkArtifact
from griptape.mixins import SerializableMixin


@define
class ActionChunkArtifact(BaseChunkArtifact, SerializableMixin):
    """An Artifact that represents a chunk of an Action.
    Can be used when streaming with Prompt Drivers that support native function calling.

    Attributes:
        tag: The tag of the action.
        name: The name of the action.
        path: The path of the action.
        input: The partial input of the action.
        index: The index of the action.
    """

    @define()
    class ActionChunk(SerializableMixin):
        tag: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
        name: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
        path: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
        input: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
        index: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})

        def __add__(self, other: ActionChunkArtifact.ActionChunk) -> ActionChunkArtifact.ActionChunk:
            if self.index == other.index:
                return ActionChunkArtifact.ActionChunk(
                    tag=(self.tag or "") + (other.tag or ""),
                    name=(self.name or "") + (other.name or ""),
                    path=(self.path or "") + (other.path or ""),
                    input=(self.input or "") + (other.input or ""),
                    index=self.index,
                )
            else:
                raise ValueError("Cannot add together actions with different indexes.")

    value: ActionChunk = field(metadata={"serializable": True})

    def __add__(self, other: BaseArtifact) -> ActionChunkArtifact:
        if isinstance(other, ActionChunkArtifact):
            return ActionChunkArtifact(value=self.value + other.value)
        else:
            raise NotImplementedError
