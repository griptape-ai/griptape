from __future__ import annotations

from attrs import define, field
from collections.abc import Sequence

from griptape.artifacts.base_artifact import BaseArtifact
from griptape.common import BaseDeltaPromptStackContent, BasePromptStackContent


@define
class ActionResultPromptStackContent(BasePromptStackContent):
    artifact: BaseArtifact = field(metadata={"serializable": True})
    action_tag: str = field(kw_only=True, metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaPromptStackContent]) -> ActionResultPromptStackContent:
        raise NotImplementedError
