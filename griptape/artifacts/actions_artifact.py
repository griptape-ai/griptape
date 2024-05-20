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
    @define(kw_only=True)
    class Action(SerializableMixin):
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
