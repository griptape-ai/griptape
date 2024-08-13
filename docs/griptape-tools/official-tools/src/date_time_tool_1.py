from griptape.structures import Agent
from griptape.tools import DateTimeTool

# Create an agent with the DateTimeTool tool
agent = Agent(tools=[DateTimeTool()])

# Fetch the current date and time
agent.run("What is the current date and time?")
