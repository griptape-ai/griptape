from griptape.structures import Agent
from griptape.tools import QueryClient, WebScraper

agent = Agent(
    tools=[
        WebScraper(off_prompt=True),
        QueryClient(off_prompt=False),
    ]
)

agent.run(
    "According to this page https://en.wikipedia.org/wiki/Elden_Ring, how many copies of Elden Ring have been sold?"
)
