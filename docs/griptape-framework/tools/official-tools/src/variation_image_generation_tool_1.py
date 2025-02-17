from griptape.drivers.image_generation.amazon_bedrock import AmazonBedrockImageGenerationDriver
from griptape.drivers.image_generation_model.bedrock_stable_diffusion import (
    BedrockStableDiffusionImageGenerationModelDriver,
)
from griptape.structures import Agent
from griptape.tools import VariationImageGenerationTool

# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(
        style_preset="pixel-art",
    ),
    model="stability.stable-diffusion-xl-v1",
)

# Create a tool configured to use the engine.
tool = VariationImageGenerationTool(
    image_generation_driver=driver,
)

# Create an agent and provide the tool to it.
Agent(tools=[tool]).run(
    "Generate a variation of the image located at tests/resources/mountain.png depicting a mountain on a winter day"
)
