from attrs import define, field
from schema import Schema

from griptape.artifacts import BaseArtifact, JsonArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class StructuredOutputTool(BaseTool):
    output_schema: Schema = field(kw_only=True)

    @activity(
        config={
            "description": "Used to provide the final response which ends this conversation.",
            "schema": lambda _self: _self.output_schema,
        }
    )
    def provide_output(self, params: dict) -> BaseArtifact:
        return JsonArtifact(params["values"])
