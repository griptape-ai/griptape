from __future__ import annotations
from abc import ABC
from collections.abc import Sequence
from typing import TYPE_CHECKING
from attrs import define, field
from griptape.mixins import SerializableMixin
from .base_delta_message_content import BaseDeltaMessageContent

if TYPE_CHECKING:
    from griptape.artifacts.base_artifact import BaseArtifact


@define
class BaseMessageContent(ABC, SerializableMixin):
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
    def from_deltas(cls, deltas: Sequence[BaseDeltaMessageContent]) -> BaseMessageContent: ...
