from __future__ import annotations

import json
from typing import TYPE_CHECKING

from attrs import define, field

from griptape.artifacts import BaseArtifact
from griptape.mixins import SerializableMixin

if TYPE_CHECKING:
    pass


@define()
class ActionCallArtifact(BaseArtifact, SerializableMixin):
    """Represents an instance of an LLM calling a Action.

    Attributes:
        tag: The tag (unique identifier) of the action.
        name: The name (Tool name) of the action.
        path: The path (Tool activity name) of the action.
        input: The input (Tool params) of the action.
    """

    @define(kw_only=True)
    class ActionCall(SerializableMixin):
        tag: str = field(metadata={"serializable": True})
        name: str = field(metadata={"serializable": True})
        path: str = field(default=None, metadata={"serializable": True})
        input: str = field(default={}, metadata={"serializable": True})

        def __str__(self) -> str:
            value = self.to_dict()

            input = value.pop("input")
            formatted_json = (
                "{" + ", ".join([f'"{k}": {json.dumps(v)}' for k, v in value.items()]) + f', "input": {input}' + "}"
            )

            return formatted_json

        def to_dict(self) -> dict:
            return {"tag": self.tag, "name": self.name, "path": self.path, "input": self.input}

    value: ActionCall = field(metadata={"serializable": True})

    def __add__(self, other: BaseArtifact) -> ActionCallArtifact:
        raise NotImplementedError
