import os
import random

import schema

from griptape.artifacts.text_artifact import TextArtifact
from griptape.drivers import GriptapeCloudToolDriver
from griptape.structures import Agent
from griptape.tools.base_tool import BaseTool
from griptape.utils.decorators import activity


class ExtendedRandomNumberGeneratorTool(BaseTool):
    @activity(
        config={
            "description": "Generates a random number in a range.",
            "schema": schema.Schema(
                {
                    "min": schema.Or(float, int),
                    "max": schema.Or(float, int),
                }
            ),
        }
    )
    def rand_range(self, values: dict) -> TextArtifact:
        return TextArtifact(random.uniform(values["min"], values["max"]))


agent = Agent(
    tools=[
        ExtendedRandomNumberGeneratorTool(
            tool_driver=GriptapeCloudToolDriver(
                api_key=os.environ["GT_CLOUD_API_KEY"],
                tool_id=os.environ["GT_CLOUD_TOOL_ID"],
            )
        )
    ],
)

agent.run("Generate a random number between 1 and 100.")
