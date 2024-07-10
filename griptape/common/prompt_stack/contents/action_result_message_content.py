from __future__ import annotations


from attrs import define, field

from griptape.common import BaseDeltaMessageContent, BaseMessageContent, ToolAction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact
    from collections.abc import Sequence


@define
class ActionResultMessageContent(BaseMessageContent):
    artifact: BaseArtifact = field(metadata={"serializable": True})
    action: ToolAction = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaMessageContent]) -> ActionResultMessageContent:
        raise NotImplementedError
