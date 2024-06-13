from __future__ import annotations

from attrs import define, field
from collections.abc import Sequence

from griptape.artifacts import TextArtifact
from griptape.common import BasePromptStackContent, BaseDeltaPromptStackContent, DeltaTextPromptStackContent


@define
class TextPromptStackContent(BasePromptStackContent):
    artifact: TextArtifact = field(metadata={"serializable": True})

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaPromptStackContent]) -> TextPromptStackContent:
        text_deltas = [delta for delta in deltas if isinstance(delta, DeltaTextPromptStackContent)]

        artifact = TextArtifact(value="".join(delta.text for delta in text_deltas))

        return cls(artifact=artifact)
