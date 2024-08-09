from griptape.structures import Agent
from griptape.tools import WebScraper

# Create an agent with the WebScraper tool
agent = Agent(tools=[WebScraper()])

agent.run(
    "According to this page https://en.wikipedia.org/wiki/Elden_Ring, how many copies of Elden Ring have been sold?"
)
