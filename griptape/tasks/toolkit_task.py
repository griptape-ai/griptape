from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from attrs import define

from griptape.mixins.actions_subtask_origin_mixin import ActionsSubtaskOriginMixin
from griptape.tasks import PromptTask

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact


@define
class ToolkitTask(PromptTask, ActionsSubtaskOriginMixin):
    def try_run(self) -> BaseArtifact:
        warnings.warn(
            "`ToolkitTask` is deprecated and will be removed in a future release. `PromptTask` is a drop-in replacement.",
            DeprecationWarning,
            stacklevel=2,
        )

        return super().try_run()
