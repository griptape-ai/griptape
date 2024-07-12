from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.common import BaseDeltaMessageContent, BaseMessageContent, TextDeltaMessageContent

if TYPE_CHECKING:
    from collections.abc import Sequence


@define
class TextMessageContent(BaseMessageContent):
    artifact: TextArtifact = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaMessageContent]) -> TextMessageContent:
        text_deltas = [delta for delta in deltas if isinstance(delta, TextDeltaMessageContent)]

        artifact = TextArtifact(value="".join(delta.text for delta in text_deltas))

        return cls(artifact=artifact)
