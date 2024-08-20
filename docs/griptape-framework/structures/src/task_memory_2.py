from griptape.structures import Agent
from griptape.tools import CalculatorTool

# Create an agent with the CalculatorTool tool
agent = Agent(tools=[CalculatorTool(off_prompt=True)])

agent.run("What is 10 raised to the power of 5?")
