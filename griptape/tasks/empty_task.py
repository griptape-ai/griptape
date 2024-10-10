from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define

from griptape.artifacts.empty_artifact import EmptyArtifact
from griptape.tasks.base_task import BaseTask

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact


@define
class EmptyTask(BaseTask):
    @property
    def input(self) -> BaseArtifact:
        return EmptyArtifact()

    def try_run(self) -> BaseArtifact:
        return self.input
