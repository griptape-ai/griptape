from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.artifacts import BaseArtifact

if TYPE_CHECKING:
    from griptape.common import ToolAction


@define()
class ActionArtifact(BaseArtifact):
    """Represents the LLM taking an action to use a Tool.

    Attributes:
        value: The Action to take. Currently only supports ToolAction.
    """

    value: ToolAction = field(metadata={"serializable": True})

    def to_text(self) -> str:
        return str(self.value)
