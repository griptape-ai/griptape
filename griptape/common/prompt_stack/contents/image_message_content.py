from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.common import BaseDeltaMessageContent, BaseMessageContent

if TYPE_CHECKING:
    from collections.abc import Sequence

    from griptape.artifacts import ImageArtifact


@define
class ImageMessageContent(BaseMessageContent):
    artifact: ImageArtifact = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaMessageContent]) -> ImageMessageContent:
        raise NotImplementedError()
