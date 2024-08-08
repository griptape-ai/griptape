from griptape.structures import Agent
from griptape.tools import Calculator

agent = Agent(input="Calculate the following: {{ args[0] }}", tools=[Calculator()])

agent.run("what's 13^7?")
print("Answer:", agent.output)
