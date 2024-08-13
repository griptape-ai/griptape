from griptape.structures import Agent
from griptape.tools import TaskMemoryTool, WebScraperTool

agent = Agent(tools=[WebScraperTool(off_prompt=True), TaskMemoryTool(off_prompt=False)])

agent.run("Based on https://www.griptape.ai/, tell me what griptape is")
