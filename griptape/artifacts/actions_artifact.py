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
        input: dict = field(
            converter=str_to_dict_converter, default=Factory(lambda: "{}"), metadata={"serializable": True}
        )
        tool: Optional[BaseTool] = field(default=None, metadata={"serializable": False})
        output: Optional[BaseArtifact] = field(default=None, metadata={"serializable": False})

        def to_dict(self):
            return {"tag": self.tag, "name": self.name, "path": self.path, "input": self.input}

    actions: list[Action] = field(default=Factory(list), metadata={"serializable": True}, kw_only=True)
    value: str = field(
        default=Factory(
            lambda self: json.dumps([action.to_dict() for action in self.actions], indent=2), takes_self=True
        ),
        metadata={"serializable": True},
    )

    def __add__(self, other: BaseArtifact) -> ActionsArtifact:
        return ActionsArtifact(self.value + other.value, actions=self.actions)
