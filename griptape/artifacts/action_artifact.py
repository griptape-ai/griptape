from __future__ import annotations

from attrs import define, field
from typing import TYPE_CHECKING

from griptape.artifacts import BaseArtifact
from griptape.mixins import SerializableMixin

if TYPE_CHECKING:
    from griptape.common import Action


@define()
class ActionArtifact(BaseArtifact, SerializableMixin):
    """Represents an instance of an LLM calling a Action.

    Attributes:
        tag: The tag (unique identifier) of the action.
        name: The name (Tool name) of the action.
        path: The path (Tool activity name) of the action.
        input: The input (Tool params) of the action.
        tool: The matched Tool of the action.
        output: The output (Tool result) of the action.
    """

    value: Action = field(metadata={"serializable": True})

    def __add__(self, other: BaseArtifact) -> ActionArtifact:
        raise NotImplementedError
