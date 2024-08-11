from griptape.structures import Agent
from griptape.tools import Calculator, TaskMemoryClient

# Create an agent with the Calculator tool
agent = Agent(tools=[Calculator(off_prompt=True), TaskMemoryClient(off_prompt=False)])

agent.run("What is the square root of 12345?")
