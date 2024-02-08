from __future__ import annotations
from attrs import define, field
from abc import ABC
from typing import Optional, Union
from collections.abc import Sequence
from griptape.artifacts import BaseArtifact
from .base_event import BaseEvent


@define
class BaseTaskEvent(BaseEvent, ABC):
    task_id: str = field(kw_only=True, metadata={"serializable": True})
    task_parent_ids: list[str] = field(kw_only=True, metadata={"serializable": True})
    task_child_ids: list[str] = field(kw_only=True, metadata={"serializable": True})

    task_input: Union[BaseArtifact, tuple[BaseArtifact, ...], tuple[BaseArtifact, Sequence[BaseArtifact]]] = field(
        kw_only=True, metadata={"serializable": True}
    )
    task_output: Optional[BaseArtifact] = field(kw_only=True, metadata={"serializable": True})
