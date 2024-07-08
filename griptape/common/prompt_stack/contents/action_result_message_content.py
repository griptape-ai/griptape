from __future__ import annotations

from collections.abc import Sequence

from attrs import define, field

from griptape.artifacts import BaseArtifact
from griptape.common import BaseDeltaMessageContent, BaseMessageContent, Action


@define
class ActionResultMessageContent(BaseMessageContent):
    artifact: BaseArtifact = field(metadata={"serializable": True})
    action: Action = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaMessageContent]) -> ActionResultMessageContent:
        raise NotImplementedError
