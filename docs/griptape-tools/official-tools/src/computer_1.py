from griptape.structures import Agent
from griptape.tools import Computer

# Initialize the Computer tool
computer = Computer()

# Create an agent with the Computer tool
agent = Agent(tools=[computer])

agent.run("Make 2 files and then list the files in the current directory")
