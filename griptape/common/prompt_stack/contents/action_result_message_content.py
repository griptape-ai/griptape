from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.common import BaseDeltaMessageContent, BaseMessageContent, ToolAction

if TYPE_CHECKING:
    from collections.abc import Sequence

    from griptape.artifacts import BaseArtifact


@define
class ActionResultMessageContent(BaseMessageContent):
    artifact: BaseArtifact = field(metadata={"serializable": True})
    action: ToolAction = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaMessageContent]) -> ActionResultMessageContent:
        raise NotImplementedError
