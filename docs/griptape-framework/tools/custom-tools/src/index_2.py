import random

from schema import Literal, Optional, Schema

from griptape.artifacts import TextArtifact
from griptape.structures import Agent
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


rng_tool = RandomNumberGenerator()

agent = Agent(tools=[rng_tool])

agent.run("generate a random number rounded to 5 decimal places")
