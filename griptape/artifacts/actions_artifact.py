from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attr import Factory, define, field

from griptape.artifacts import BaseArtifact, TextArtifact

if TYPE_CHECKING:
    from griptape.tools import BaseTool


@define
class ActionsArtifact(TextArtifact):
    @define(kw_only=True)
    class Action:
        tag: str = field()
        name: str = field()
        path: Optional[str] = field(default=None)
        input: dict = field()
        tool: Optional[BaseTool] = field(default=None)

    value: str = field(metadata={"serializable": True})
    actions: list[Action] = field(default=Factory(list), metadata={"serializable": True}, kw_only=True)

    def __add__(self, other: BaseArtifact) -> ActionsArtifact:
        return ActionsArtifact(self.value + other.value, actions=self.actions)
