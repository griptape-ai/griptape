from griptape.structures import Agent
from griptape.tools import ComputerTool

# Initialize the ComputerTool tool
computer = ComputerTool()

# Create an agent with the ComputerTool tool
agent = Agent(tools=[computer])

agent.run("Make 2 files and then list the files in the current directory")
