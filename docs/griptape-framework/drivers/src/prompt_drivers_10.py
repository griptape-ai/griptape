from griptape.drivers.prompt.ollama import OllamaPromptDriver
from griptape.structures import Agent
from griptape.tools import CalculatorTool

agent = Agent(
    prompt_driver=OllamaPromptDriver(
        model="llama3.1",
    ),
    tools=[CalculatorTool()],
)
agent.run("What is (192 + 12) ^ 4")
