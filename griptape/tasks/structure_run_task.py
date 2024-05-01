from __future__ import annotations

from attr import define, field
from typing import TYPE_CHECKING

from griptape.artifacts import BaseArtifact, ErrorArtifact
from griptape.tasks import BaseTextInputTask

if TYPE_CHECKING:
    from griptape.structures import Structure


@define
class StructureRunTask(BaseTextInputTask):
    """Task to run a Structure.

    Attributes:
        structure_to_run: Structure to run.
    """

    structure_to_run: Structure = field(kw_only=True)

    def run(self) -> BaseArtifact:
        self.structure_to_run.run(self.input)

        if self.structure_to_run.output_task.output is not None:
            return self.structure_to_run.output_task.output
        else:
            return ErrorArtifact("Structure did not produce any output.")
