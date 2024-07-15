from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.events.base_event import BaseEvent

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact


@define
class FinishStructureRunEvent(BaseEvent):
    structure_id: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": True})
    output_task_input: BaseArtifact = field(kw_only=True, metadata={"serializable": True})
    output_task_output: Optional[BaseArtifact] = field(kw_only=True, metadata={"serializable": True})
