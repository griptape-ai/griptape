from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.common import BaseDeltaMessageContent, BaseMessageContent

if TYPE_CHECKING:
    from collections.abc import Sequence

    from griptape.artifacts import GenericArtifact


@define
class GenericMessageContent(BaseMessageContent):
    artifact: GenericArtifact = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaMessageContent]) -> GenericMessageContent:
        raise NotImplementedError()
