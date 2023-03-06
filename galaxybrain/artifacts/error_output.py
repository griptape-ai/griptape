from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Optional
from attrs import define, field
from galaxybrain.artifacts import StructureArtifact


if TYPE_CHECKING:
    from galaxybrain.steps import Step


@define(frozen=True)
class ErrorOutput(StructureArtifact):
    step: Optional[Step] = field(default=None, kw_only=True)
