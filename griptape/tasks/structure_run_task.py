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
        target_structure: Structure to run.
    """

    target_structure: Structure = field(kw_only=True)

    def run(self) -> BaseArtifact:
        self.target_structure.run(self.input)

        if self.target_structure.output_task.output is not None:
            return self.target_structure.output_task.output
        else:
            return ErrorArtifact("Structure did not produce any output.")
