import os

from griptape.structures import Agent
from griptape.tools.griptape_cloud_tool.tool import GriptapeCloudToolTool

agent = Agent(
    tools=[
        GriptapeCloudToolTool(  # Tool is configured as a random number generator
            tool_id=os.environ["GT_CLOUD_TOOL_ID"],
        )
    ]
)
agent.run("Generate a number between 1 and 10")
