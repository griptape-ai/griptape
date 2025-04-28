from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.structures import Agent
from griptape.tools import ImageQueryTool

driver = OpenAiChatPromptDriver(model="gpt-4.1")

# Create an Image Query Tool configured to use the engine.
tool = ImageQueryTool(
    prompt_driver=driver,
)

# Create an agent and provide the tool to it.
Agent(tools=[tool]).run("Describe the weather in the image tests/resources/mountain.png in one word.")
