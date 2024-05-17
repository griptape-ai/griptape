from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional, Any

from attr import Factory, define, field

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.tools import BaseTool


def str_to_dict_converter(data: Any):
    if isinstance(data, dict):
        return data
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise Exception(f"Activity input JSON validation error: {e}")


@define
class ActionsArtifact(TextArtifact):
    @define(kw_only=True)
    class Action(SerializableMixin):
        tag: str = field(metadata={"serializable": True})
        name: str = field(metadata={"serializable": True})
        path: Optional[str] = field(default=None, metadata={"serializable": True})
        input: dict = field(default={}, metadata={"serializable": True})
        tool: Optional[BaseTool] = field(default=None, metadata={"serializable": False})
        output: Optional[BaseArtifact] = field(default=None, metadata={"serializable": False})

        _partial_input: str = field(default="", metadata={"serializable": False}, alias="partial_input")

        def to_dict(self) -> dict:
            try:
                input = json.loads(self._partial_input)
            except json.JSONDecodeError:
                input = self._partial_input

            return {"tag": self.tag, "name": self.name, "path": self.path, "input": input}

        def __add__(self, other: ActionsArtifact.Action) -> ActionsArtifact.Action:
            return ActionsArtifact.Action(
                tag=self.tag + other.tag,
                name=self.name + other.name,
                path=(self.path or "") + (other.path or ""),
                partial_input=self._partial_input + other._partial_input,
            )

    actions: list[Action] = field(default=Factory(list), metadata={"serializable": True}, kw_only=True)
    value: str = field(
        default=Factory(
            lambda self: json.dumps([action.to_dict() for action in self.actions], indent=2), takes_self=True
        ),
        metadata={"serializable": True},
    )

    def __add__(self, other: BaseArtifact) -> ActionsArtifact:
        if isinstance(other, ActionsArtifact):
            # When streaming we receive the actions in chunks, so we need to merge them
            added_actions = []
            for action, other_action in zip(self.actions, other.actions):
                if action.tag != other_action.tag:
                    raise ValueError("Cannot add ActionsArtifacts with different tags")
                added_actions.append(action + other_action)

            return ActionsArtifact(self.value + other.value, actions=added_actions)
        else:
            return ActionsArtifact(self.value + other.value, actions=self.actions)
