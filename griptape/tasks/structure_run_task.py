from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.tasks import BaseMultiTextInputTask

if TYPE_CHECKING:
    from griptape.artifacts import BaseArtifact
    from griptape.drivers.structure_run.base_structure_run_driver import BaseStructureRunDriver


@define
class StructureRunTask(BaseMultiTextInputTask):
    """Task to run a Structure.

    Attributes:
        driver: Driver to run the Structure.
    """

    driver: BaseStructureRunDriver = field(kw_only=True)

    def run(self) -> BaseArtifact:
        return self.driver.run(*self.input)
