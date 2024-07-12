from __future__ import annotations


from attrs import define, field

from griptape.common import BaseDeltaMessageContent, BaseMessageContent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from griptape.artifacts import GenericArtifact
    from collections.abc import Sequence


@define
class GenericMessageContent(BaseMessageContent):
    artifact: GenericArtifact = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaMessageContent]) -> GenericMessageContent:
        raise NotImplementedError()
