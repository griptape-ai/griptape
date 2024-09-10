from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.artifacts import BaseArtifact
from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.common import ToolAction


@define()
class ActionArtifact(BaseArtifact, SerializableMixin):
    value: ToolAction = field(metadata={"serializable": True})

    def __add__(self, other: BaseArtifact) -> ActionArtifact:
        raise NotImplementedError
