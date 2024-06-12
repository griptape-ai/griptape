from __future__ import annotations

from abc import ABC
from collections.abc import Sequence

from attrs import define, field

from griptape.artifacts.base_artifact import BaseArtifact
from griptape.mixins import SerializableMixin

from .base_delta_prompt_stack_content import BaseDeltaPromptStackContent


@define
class BasePromptStackContent(ABC, SerializableMixin):
    artifact: BaseArtifact = field(metadata={"serializable": True})

    def to_text(self) -> str:
        return str(self.artifact)

    def __str__(self) -> str:
        return self.artifact.to_text()

    def __bool__(self) -> bool:
        return bool(self.artifact)

    def __len__(self) -> int:
        return len(self.artifact)

    @classmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaPromptStackContent]) -> BasePromptStackContent: ...
