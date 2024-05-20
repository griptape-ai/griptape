from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional

from attr import Factory, define, field

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.tools import BaseTool


@define
class ActionsArtifact(TextArtifact):
    """An Artifact that represents a list of Actions.
    Can be used with Prompt Drivers that support native function calling.

    Attributes:
        actions: The list of actions.
        value: The value of the artifact.
    """

    @define(kw_only=True)
    class Action(SerializableMixin):
        """Represents an instance of an LLM taking an action to use a Tool.

        Attributes:
            tag: The tag (unique identifier) of the action.
            name: The name (Tool name) of the action.
            path: The path (Tool activity name) of the action.
            input: The input (Tool params) of the action.
            tool: The tool used in the action.
            output: The output of the action execution.
        """

        tag: str = field(metadata={"serializable": True})
        name: str = field(metadata={"serializable": True})
        path: Optional[str] = field(default=None, metadata={"serializable": True})
        input: dict = field(default={}, metadata={"serializable": True})
        tool: Optional[BaseTool] = field(default=None, metadata={"serializable": False})
        output: Optional[BaseArtifact] = field(default=None, metadata={"serializable": False})

        def to_dict(self) -> dict:
            return {"tag": self.tag, "name": self.name, "path": self.path, "input": self.input}

    actions: list[Action] = field(default=Factory(list), metadata={"serializable": True}, kw_only=True)
    value: str = field(
        default=Factory(
            lambda self: json.dumps([action.to_dict() for action in self.actions], indent=2), takes_self=True
        ),
        metadata={"serializable": True},
    )
