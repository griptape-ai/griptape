from typing import Optional, Union
from collections.abc import Sequence

from attrs import define, field

from griptape.artifacts import BaseArtifact
from griptape.events.base_event import BaseEvent


@define
class StartStructureRunEvent(BaseEvent):
    input_task_input: Union[
        BaseArtifact, tuple[BaseArtifact, ...], tuple[BaseArtifact, Sequence[BaseArtifact]]
    ] = field(kw_only=True, metadata={"serializable": True})
    input_task_output: Optional[BaseArtifact] = field(kw_only=True, metadata={"serializable": True})
