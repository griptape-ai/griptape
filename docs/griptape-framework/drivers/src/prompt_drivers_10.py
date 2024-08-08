from griptape.config import StructureConfig
from griptape.drivers import OllamaPromptDriver
from griptape.structures import Agent
from griptape.tools import Calculator

agent = Agent(
    config=StructureConfig(
        prompt_driver=OllamaPromptDriver(
            model="llama3.1",
        ),
    ),
    tools=[Calculator()],
)
agent.run("What is (192 + 12) ^ 4")
