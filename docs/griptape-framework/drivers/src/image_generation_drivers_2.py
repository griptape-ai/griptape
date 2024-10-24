from griptape.drivers import AmazonBedrockImageGenerationDriver, BedrockStableDiffusionImageGenerationModelDriver
from griptape.structures import Agent
from griptape.tools import PromptImageGenerationTool

model_driver = BedrockStableDiffusionImageGenerationModelDriver(
    style_preset="pixel-art",
)

driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=model_driver,
    model="stability.stable-diffusion-xl-v0",
)


agent = Agent(
    tools=[
        PromptImageGenerationTool(image_generation_driver=driver),
    ]
)

agent.run("Generate an image of a dog riding a skateboard")
