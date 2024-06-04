from typing import Optional

from attrs import define, field

from griptape.artifacts import BaseArtifact
from griptape.events.base_event import BaseEvent


@define
class StartStructureRunEvent(BaseEvent):
    structure_id: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": True})
    input_task_input: BaseArtifact = field(kw_only=True, metadata={"serializable": True})
    input_task_output: Optional[BaseArtifact] = field(kw_only=True, metadata={"serializable": True})
