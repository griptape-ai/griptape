from __future__ import annotations
from typing import TYPE_CHECKING

from attrs import define, field

from griptape.artifacts import BaseArtifact, ErrorArtifact
from griptape.drivers.structure_run.base_structure_run_driver import BaseStructureRunDriver

if TYPE_CHECKING:
    from griptape.structures import Structure


@define
class LocalStructureRunDriver(BaseStructureRunDriver):
    structure: Structure = field(kw_only=True)

    def try_run(self, *args) -> BaseArtifact:
        self.structure.run(*args)

        if self.structure.output_task.output is not None:
            return self.structure.output_task.output
        else:
            return ErrorArtifact("Structure did not produce any output.")
