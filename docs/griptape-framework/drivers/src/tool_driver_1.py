import os

from griptape.drivers import GriptapeCloudToolDriver
from griptape.structures import Agent
from griptape.tools import BaseTool


class RandomNumberGeneratorTool(BaseTool): ...


agent = Agent(
    tools=[
        RandomNumberGeneratorTool(
            tool_driver=GriptapeCloudToolDriver(
                api_key=os.environ["GT_CLOUD_API_KEY"],
                tool_id=os.environ["GT_CLOUD_TOOL_ID"],
            )
        )
    ],
)

agent.run("Generate a random number to 5 decimal places.")
