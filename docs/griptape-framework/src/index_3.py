from griptape.structures import Agent
from griptape.tools import Calculator

calculator = Calculator()

agent = Agent(tools=[calculator])

agent.run("what is 7^12")
print("Answer:", agent.output)
