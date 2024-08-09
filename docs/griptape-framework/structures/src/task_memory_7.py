from griptape.structures import Agent
from griptape.tools import WebScraper

agent = Agent(
    tools=[
        WebScraper(off_prompt=True)  # `off_prompt=True` will store the data in Task Memory
        # Missing a Tool that can read from Task Memory
    ]
)
agent.run(
    "According to this page https://en.wikipedia.org/wiki/San_Francisco, what is the population of San Francisco?"
)
