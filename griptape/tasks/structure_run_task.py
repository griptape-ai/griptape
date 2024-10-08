from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.artifacts.list_artifact import ListArtifact
from griptape.tasks.prompt_task import PromptTask

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact
    from griptape.drivers.structure_run.base_structure_run_driver import BaseStructureRunDriver


@define
class StructureRunTask(PromptTask):
    """Task to run a Structure.

    Attributes:
        driver: Driver to run the Structure.
    """

    driver: BaseStructureRunDriver = field(kw_only=True)

    def run(self) -> BaseArtifact:
        if isinstance(self.input, ListArtifact):
            return self.driver.run(*self.input.value)
        else:
            return self.driver.run(self.input)
