from griptape.structures import Agent
from griptape.tools import TaskMemoryTool, WebScraperTool

agent = Agent(
    tools=[
        WebScraperTool(off_prompt=True),
        TaskMemoryTool(off_prompt=False),
    ]
)

agent.run(
    "According to this page https://en.wikipedia.org/wiki/Elden_Ring, how many copies of Elden Ring have been sold?"
)
