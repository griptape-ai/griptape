from __future__ import annotations


from attrs import define, field

from griptape.common import BaseDeltaMessageContent, BaseMessageContent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from griptape.artifacts import ImageArtifact
    from collections.abc import Sequence


@define
class ImageMessageContent(BaseMessageContent):
    artifact: ImageArtifact = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaMessageContent]) -> ImageMessageContent:
        raise NotImplementedError()
