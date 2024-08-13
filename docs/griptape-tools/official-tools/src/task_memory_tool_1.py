from griptape.structures import Agent
from griptape.tools import TaskMemoryTool, WebScraperTool

Agent(tools=[WebScraperTool(off_prompt=True), TaskMemoryTool(off_prompt=False)])
