from __future__ import annotations

from attrs import define, field
from typing import Sequence

from griptape.artifacts.action_call_artifact import ActionCallArtifact
from griptape.common import BasePromptStackContent, BaseDeltaPromptStackContent
from griptape.common import DeltaActionCallPromptStackContent


@define
class ActionCallPromptStackContent(BasePromptStackContent):
    artifact: ActionCallArtifact = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaPromptStackContent]) -> ActionCallPromptStackContent:
        action_call_deltas = [delta for delta in deltas if isinstance(delta, DeltaActionCallPromptStackContent)]

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
            action = ActionCallArtifact.ActionCall(tag=tag, name=name, path=path, input=input)
        else:
            raise ValueError("Missing required fields for ActionCallArtifact.Action")

        artifact = ActionCallArtifact(value=action)

        return cls(artifact=artifact)
