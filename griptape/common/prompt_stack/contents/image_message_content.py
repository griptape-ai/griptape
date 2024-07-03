from __future__ import annotations

from collections.abc import Sequence

from attrs import define, field

from griptape.artifacts import ImageArtifact
from griptape.common import BaseDeltaMessageContent, BaseMessageContent


@define
class ImageMessageContent(BaseMessageContent):
    artifact: ImageArtifact = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaMessageContent]) -> ImageMessageContent:
        raise NotImplementedError()
