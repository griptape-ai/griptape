from __future__ import annotations

from collections.abc import Sequence

from attrs import define, field

from griptape.artifacts import BaseArtifact, ActionArtifact
from griptape.common import BaseDeltaPromptStackContent, BasePromptStackContent


@define
class ActionResultPromptStackContent(BasePromptStackContent):
    artifact: BaseArtifact = field(metadata={"serializable": True})
    action: ActionArtifact.Action = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaPromptStackContent]) -> ActionResultPromptStackContent:
        raise NotImplementedError
