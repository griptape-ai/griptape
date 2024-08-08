import os

from griptape.drivers import LeonardoImageGenerationDriver
from griptape.engines import PromptImageGenerationEngine
from griptape.structures import Agent
from griptape.tools import PromptImageGenerationClient

driver = LeonardoImageGenerationDriver(
    model=os.environ["LEONARDO_MODEL_ID"],
    api_key=os.environ["LEONARDO_API_KEY"],
    image_width=512,
    image_height=1024,
)

engine = PromptImageGenerationEngine(image_generation_driver=driver)

agent = Agent(
    tools=[
        PromptImageGenerationClient(engine=engine),
    ]
)

agent.run("Generate a watercolor painting of a dog riding a skateboard")
