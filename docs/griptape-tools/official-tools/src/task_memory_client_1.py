from griptape.structures import Agent
from griptape.tools import TaskMemoryClient, WebScraper

Agent(tools=[WebScraper(off_prompt=True), TaskMemoryClient(off_prompt=False)])
