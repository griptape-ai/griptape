import random

from schema import Literal, Optional, Schema

from griptape.artifacts import TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


class RandomNumberGenerator(BaseTool):
    @activity(
        config={
            "description": "Can be used to generate random numbers",
            "schema": Schema(
                {Optional(Literal("decimals", description="Number of decimals to round the random number to")): int}
            ),
        }
    )
    def generate(self, params: dict) -> TextArtifact:
        return TextArtifact(str(round(random.random(), params["values"].get("decimals"))))


RandomNumberGenerator()
