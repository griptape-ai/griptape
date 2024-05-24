from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define, field
from typing import Optional
from griptape.mixins import SerializableMixin
from griptape.artifacts import BaseArtifact

if TYPE_CHECKING:
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
        tag: str = field(metadata={"serializable": True})
        name: str = field(metadata={"serializable": True})
        path: Optional[str] = field(default=None, metadata={"serializable": True})
        input: dict = field(default={}, metadata={"serializable": True})
        tool: Optional[BaseTool] = field(default=None, metadata={"serializable": False})
        output: Optional[BaseArtifact] = field(default=None, metadata={"serializable": False})

        def __str__(self) -> str:
            return f"{self.name} {self.path} {self.input} {self.output}"

    value: Action = field(metadata={"serializable": True})

    def __add__(self, other: BaseArtifact) -> ActionArtifact:
        raise NotImplementedError
