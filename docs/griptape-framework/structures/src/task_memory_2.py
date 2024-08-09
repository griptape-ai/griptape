from griptape.structures import Agent
from griptape.tools import Calculator

# Create an agent with the Calculator tool
agent = Agent(tools=[Calculator(off_prompt=True)])

agent.run("What is 10 raised to the power of 5?")
