from griptape.drivers import OpenAiImageGenerationDriver
from griptape.engines import PromptImageGenerationEngine
from griptape.structures import Agent
from griptape.tools import PromptImageGenerationClient

driver = OpenAiImageGenerationDriver(
    model="dall-e-2",
)

engine = PromptImageGenerationEngine(image_generation_driver=driver)

agent = Agent(
    tools=[
        PromptImageGenerationClient(engine=engine),
    ]
)

agent.run("Generate a watercolor painting of a dog riding a skateboard")
