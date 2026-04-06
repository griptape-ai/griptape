from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.events.base_event import BaseEvent

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact


@define
class FinishStructureRunEvent(BaseEvent):
    structure_id: str | None = field(kw_only=True, default=None, metadata={"serializable": True})
    output_task_input: BaseArtifact | None = field(kw_only=True, default=None, metadata={"serializable": True})
    output_task_output: BaseArtifact | None = field(kw_only=True, default=None, metadata={"serializable": True})
