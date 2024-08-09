from griptape.structures import Agent
from griptape.tools import DateTime

# Create an agent with the DateTime tool
agent = Agent(tools=[DateTime()])

# Fetch the current date and time
agent.run("What is the current date and time?")
