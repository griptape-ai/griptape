from griptape.drivers import AmazonBedrockImageGenerationDriver, BedrockStableDiffusionImageGenerationModelDriver
from griptape.engines import PromptImageGenerationEngine
from griptape.structures import Agent
from griptape.tools import PromptImageGenerationClient

model_driver = BedrockStableDiffusionImageGenerationModelDriver(
    style_preset="pixel-art",
)

driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=model_driver,
    model="stability.stable-diffusion-xl-v0",
)

engine = PromptImageGenerationEngine(image_generation_driver=driver)

agent = Agent(
    tools=[
        PromptImageGenerationClient(engine=engine),
    ]
)

agent.run("Generate an image of a dog riding a skateboard")
