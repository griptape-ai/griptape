from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from attrs import define, field

from griptape.mixins import SerializableMixin

if TYPE_CHECKING:
    from collections.abc import Sequence

    from griptape.artifacts.base_artifact import BaseArtifact

    from .base_delta_message_content import BaseDeltaMessageContent


@define
class BaseMessageContent(ABC, SerializableMixin):
    artifact: BaseArtifact = field(metadata={"serializable": True})

    def __str__(self) -> str:
        return self.artifact.to_text()

    def __bool__(self) -> bool:
        return bool(self.artifact)

    def __len__(self) -> int:
        return len(self.artifact)

    def to_text(self) -> str:
        return str(self.artifact)

    @classmethod
    @abstractmethod
    def from_deltas(cls, deltas: Sequence[BaseDeltaMessageContent]) -> BaseMessageContent: ...
