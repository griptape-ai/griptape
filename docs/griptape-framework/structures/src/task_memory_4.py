from griptape.structures import Agent
from griptape.tools import WebScraperTool

# Create an agent with the WebScraperTool tool
agent = Agent(tools=[WebScraperTool()])

agent.run(
    "According to this page https://en.wikipedia.org/wiki/Elden_Ring, how many copies of Elden Ring have been sold?"
)
