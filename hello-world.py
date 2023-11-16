from griptape.structures import Agent
from griptape.tools import TaskMemoryClient, WebScraper

agent = Agent(tools=[WebScraper(), TaskMemoryClient(off_prompt=False)])

agent.run("Based on the website https://griptape.ai, tell me what griptape is.")
