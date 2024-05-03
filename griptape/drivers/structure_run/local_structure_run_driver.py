from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from attrs import define, field

from griptape.artifacts import BaseArtifact, InfoArtifact
from griptape.drivers.structure_run.base_structure_run_driver import BaseStructureRunDriver

if TYPE_CHECKING:
    from griptape.structures import Structure


@define
class LocalStructureRunDriver(BaseStructureRunDriver):
    structure_factory_fn: Callable[[], Structure] = field(kw_only=True)

    def try_run(self, *args: BaseArtifact) -> BaseArtifact:
        structure_factory_fn = self.structure_factory_fn().run(*[arg.value for arg in args])

        if structure_factory_fn.output_task.output is not None:
            return structure_factory_fn.output_task.output
        else:
            return InfoArtifact("No output found in response")
