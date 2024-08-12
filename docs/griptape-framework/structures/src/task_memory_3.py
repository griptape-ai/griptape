from griptape.structures import Agent
from griptape.tools import Calculator, PromptSummaryClient

# Create an agent with the Calculator tool
agent = Agent(tools=[Calculator(off_prompt=True), PromptSummaryClient(off_prompt=False)])

agent.run("What is the square root of 12345?")
