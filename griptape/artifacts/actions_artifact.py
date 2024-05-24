from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional

from attr import Factory, define, field
from griptape.artifacts import TextArtifact

if TYPE_CHECKING:
    from griptape.artifacts import ActionArtifact


@define
class ActionsArtifact(TextArtifact):
    """An Artifact that represents a list of Actions.
    Can be used with Prompt Drivers that support native function calling.

    Attributes:
        actions: The list of actions.
        value: Optional text associated with the actions. Can represent the Chain of Thought associated with the action calls, or further instruction with the action results.
    """

    actions: list[ActionArtifact.Action] = field(default=Factory(list), metadata={"serializable": True}, kw_only=True)
    value: Optional[str] = field(default=None, metadata={"serializable": True})

    def to_text(self) -> str:
        text = ""
        if self.value is not None:
            text += f"{self.value}\n"
        if self.actions:
            text += f"{json.dumps([action.to_dict() for action in self.actions], indent=2)}"

        return text
