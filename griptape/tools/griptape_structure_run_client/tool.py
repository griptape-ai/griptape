from __future__ import annotations

from attr import define, field
from schema import Literal, Schema

from griptape.artifacts import BaseArtifact
from griptape.drivers.structure_run.base_structure_run_driver import BaseStructureRunDriver
from griptape.tools.base_tool import BaseTool
from griptape.utils.decorators import activity


@define
class GriptapeStructureRunClient(BaseTool):
    """
    Attributes:
        description: A description of what the Structure does.
        driver: Driver to run the Structure.
    """

    description: str = field(kw_only=True)
    driver: BaseStructureRunDriver = field(kw_only=True)

    @activity(
        config={
            "description": "Can be used to run a Griptape Structure with the following description: {{ self.description }}",
            "schema": Schema({Literal("args", description="Arguments to pass to the Structure Run."): str}),
        }
    )
    def run_structure(self, params: dict) -> BaseArtifact:
        args: str = params["values"]["args"]

        return self.driver.run(args)
