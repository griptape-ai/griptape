from __future__ import annotations

from typing import TYPE_CHECKING, Union

from attrs import define, field

from griptape.common import BaseDeltaMessageContent, BaseMessageContent

if TYPE_CHECKING:
    from collections.abc import Sequence

    from griptape.artifacts import ImageArtifact, ImageUrlArtifact


@define
class ImageMessageContent(BaseMessageContent):
    artifact: Union[ImageArtifact, ImageUrlArtifact] = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaMessageContent]) -> ImageMessageContent:
        raise NotImplementedError
