from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional, Any

from attr import Factory, define, field

from griptape.artifacts import BaseArtifact, TextArtifact

if TYPE_CHECKING:
    from griptape.tools import BaseTool


def str_to_dict_converter(data: Any):
    if isinstance(data, dict):
        return data
    try:
        return json.loads(data)
    except Exception as e:  # TODO: more precise exception for json parsing
        raise Exception(f"Activity input JSON validation error: {e}")


@define
class ActionsArtifact(TextArtifact):
    @define(kw_only=True)
    class Action:
        tag: str = field()
        name: str = field()
        path: Optional[str] = field(default=None)
        input: dict = field(converter=str_to_dict_converter, default=Factory(lambda: "{}"))
        tool: Optional[BaseTool] = field(default=None)

    value: str = field(metadata={"serializable": True})
    actions: list[Action] = field(default=Factory(list), metadata={"serializable": True}, kw_only=True)

    def __add__(self, other: BaseArtifact) -> ActionsArtifact:
        return ActionsArtifact(self.value + other.value, actions=self.actions)
