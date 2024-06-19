from __future__ import annotations

import json
from collections.abc import Sequence

from attrs import define, field

from griptape.artifacts import ActionArtifact
from griptape.common import BaseDeltaPromptStackContent, BasePromptStackContent, ActionCallDeltaPromptStackContent


@define
class ActionCallPromptStackContent(BasePromptStackContent):
    artifact: ActionArtifact = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaPromptStackContent]) -> ActionCallPromptStackContent:
        action_call_deltas = [delta for delta in deltas if isinstance(delta, ActionCallDeltaPromptStackContent)]

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
            if delta.delta_input is not None:
                input += delta.delta_input

        if tag is not None and name is not None and path is not None:
            try:
                parsed_input = json.loads(input)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON input for ActionArtifact.Action")
            action = ActionArtifact.Action(tag=tag, name=name, path=path, input=parsed_input)
        else:
            raise ValueError("Missing required fields for ActionArtifact.Action")

        artifact = ActionArtifact(value=action)

        return cls(artifact=artifact)
