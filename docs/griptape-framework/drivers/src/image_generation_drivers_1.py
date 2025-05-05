from griptape.drivers.image_generation.openai import OpenAiImageGenerationDriver
from griptape.structures import Agent
from griptape.tools import PromptImageGenerationTool

driver = OpenAiImageGenerationDriver(
    model="gpt-image-1",
)

agent = Agent(
    tools=[
        PromptImageGenerationTool(image_generation_driver=driver),
    ]
)

agent.run("Generate a watercolor painting of a dog riding a skateboard")
