from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from .base_event import BaseEvent

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact


@define
class BaseTaskEvent(BaseEvent, ABC):
    task_id: str = field(kw_only=True, metadata={"serializable": True})
    task_parent_ids: list[str] = field(kw_only=True, metadata={"serializable": True})
    task_child_ids: list[str] = field(kw_only=True, metadata={"serializable": True})

    task_input: BaseArtifact = field(kw_only=True, metadata={"serializable": True})
    task_output: Optional[BaseArtifact] = field(kw_only=True, metadata={"serializable": True})
