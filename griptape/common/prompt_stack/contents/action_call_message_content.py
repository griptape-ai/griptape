from __future__ import annotations

import json
from collections.abc import Sequence

from attrs import define, field

from griptape.common import Action
from griptape.artifacts import ActionArtifact
from griptape.common import BaseDeltaMessageContent, BaseMessageContent, ActionCallDeltaMessageContent


@define
class ActionCallMessageContent(BaseMessageContent):
    artifact: ActionArtifact = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaMessageContent]) -> ActionCallMessageContent:
        action_call_deltas = [delta for delta in deltas if isinstance(delta, ActionCallDeltaMessageContent)]

        tag = None
        name = None
        path = None
        input = ""

        for delta in action_call_deltas:
            if delta.tag is not None:
                tag = delta.tag
            if delta.name is not None:
                name = delta.name
            if delta.path is not None:
                path = delta.path
            if delta.partial_input is not None:
                input += delta.partial_input

        if tag is not None and name is not None and path is not None:
            try:
                parsed_input = json.loads(input)
            except json.JSONDecodeError as exc:
                raise ValueError("Invalid JSON input for Action") from exc
            action = Action(tag=tag, name=name, path=path, input=parsed_input)
        else:
            raise ValueError("Missing required fields for Action")

        artifact = ActionArtifact(value=action)

        return cls(artifact=artifact)
