import os

from griptape.drivers.image_generation.leonardo import LeonardoImageGenerationDriver
from griptape.structures import Agent
from griptape.tools import PromptImageGenerationTool

driver = LeonardoImageGenerationDriver(
    model=os.environ["LEONARDO_MODEL_ID"],
    api_key=os.environ["LEONARDO_API_KEY"],
    image_width=512,
    image_height=1024,
)


agent = Agent(
    tools=[
        PromptImageGenerationTool(image_generation_driver=driver),
    ]
)

agent.run("Generate a watercolor painting of a dog riding a skateboard")
