from griptape.structures import Agent
from griptape.tools import Calculator

# Create an agent with the Calculator tool
agent = Agent(tools=[Calculator()])

# Run the agent with a task to perform the arithmetic calculation of \(10^5\)
agent.run("What is 10 raised to the power of 5?")
