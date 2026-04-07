from griptape.structures import Agent
from griptape.tools import CalculatorTool

# Create an agent with the CalculatorTool tool
agent = Agent(tools=[CalculatorTool()])

# Run the agent with a task to perform the arithmetic calculation of \(10^5\)
agent.run("What is 10 raised to the power of 5?")
