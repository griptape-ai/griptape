from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attrs import field, define
from griptape.memory.meta import BaseMetaEntry

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact


@define
class ControlFlowMetaEntry(BaseMetaEntry):
    type: str = field(default=__name__, kw_only=True, metadata={"serializable": False})
    input_tasks: list[str] = field(factory=list, kw_only=True)
    output_tasks: list[str] = field(factory=list, kw_only=True)
    output: Optional[BaseArtifact] = field(default=None, kw_only=True)
