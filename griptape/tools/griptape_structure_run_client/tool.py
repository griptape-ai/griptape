from __future__ import annotations

from typing import TYPE_CHECKING
from attr import define, field
from schema import Literal, Schema

from griptape.artifacts import ErrorArtifact, BaseArtifact
from griptape.tools.base_tool import BaseTool
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.structures import Structure


@define
class GriptapeStructureRunClient(BaseTool):
    """
    Attributes:
        description: A description of what the Structure does.
        structure: A Structure to run.
    """

    description: str = field(kw_only=True)
    structure: Structure = field(kw_only=True)

    @activity(
        config={
            "description": "Can be used to Run a Griptape Structure with the following description: {{ self.description }}",
            "schema": Schema({Literal("args", description="Arguments to pass to the Structure Run"): str}),
        }
    )
    def run_structure(self, params: dict) -> BaseArtifact:
        args: str = params["values"]["args"]

        self.structure.run(args)

        if self.structure.output_task.output is not None:
            return self.structure.output_task.output
        else:
            return ErrorArtifact("Structure did not produce any output.")
