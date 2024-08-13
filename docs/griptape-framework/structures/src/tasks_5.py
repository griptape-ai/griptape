from griptape.structures import Agent
from griptape.tasks import ToolTask
from griptape.tools import CalculatorTool

# Initialize the agent and add a task
agent = Agent()
agent.add_task(ToolTask(tool=CalculatorTool()))

# Run the agent with a prompt
agent.run("Give me the answer for 5*4.")
