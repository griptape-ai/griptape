from griptape.structures import Agent
from griptape.tools import DateTimeTool

agent = Agent(tools=[DateTimeTool()])

agent.run("What day is 5 days past christmas in 2026?")
