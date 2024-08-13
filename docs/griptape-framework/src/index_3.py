from griptape.structures import Agent
from griptape.tools import CalculatorTool

calculator = CalculatorTool()

agent = Agent(tools=[calculator])

agent.run("what is 7^12")
print("Answer:", agent.output)
