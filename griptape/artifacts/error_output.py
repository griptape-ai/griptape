from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Optional
from attr import define, field
from griptape.artifacts import BaseArtifact


if TYPE_CHECKING:
    from griptape.tasks import BaseTask


@define(frozen=True)
class ErrorOutput(BaseArtifact):
    value: Optional[str] = field()
    exception: Optional[Exception] = field(default=None, kw_only=True)
    task: Optional[BaseTask] = field(default=None, kw_only=True)
