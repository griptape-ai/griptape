from griptape.structures import Agent
from griptape.tools import CalculatorTool, PromptSummaryTool

# Create an agent with the Calculator tool
agent = Agent(tools=[CalculatorTool(off_prompt=True), PromptSummaryTool(off_prompt=False)])

agent.run("What is the square root of 12345?")
