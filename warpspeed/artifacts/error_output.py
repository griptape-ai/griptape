from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Optional
from attrs import define, field
from warpspeed.artifacts import StructureArtifact


if TYPE_CHECKING:
    from warpspeed.steps import Step


@define(frozen=True)
class ErrorOutput(StructureArtifact):
    exception: Optional[Exception] = field(default=None, kw_only=True)
    step: Optional[Step] = field(default=None, kw_only=True)
