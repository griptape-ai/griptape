import os

from griptape.drivers import GriptapeCloudToolDriver
from griptape.structures import Agent
from griptape.tools import BaseTool


class RandomNumberGeneratorTool(BaseTool): ...


tool = RandomNumberGeneratorTool()
driver = GriptapeCloudToolDriver(
    api_key=os.environ["GT_CLOUD_API_KEY"],
    tool_id=os.environ["GT_CLOUD_TOOL_ID"],
)
driver.initialize_tool(tool)

agent = Agent(
    tools=[tool],
)

agent.run("Generate a random number to 5 decimal places.")
