from griptape.drivers.image_generation.amazon_bedrock import AmazonBedrockImageGenerationDriver
from griptape.drivers.image_generation_model.bedrock_stable_diffusion import (
    BedrockStableDiffusionImageGenerationModelDriver,
)
from griptape.structures import Agent
from griptape.tools import OutpaintingImageGenerationTool

# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(),
    model="stability.stable-diffusion-xl-v0",
)

# Create a tool configured to use the engine.
tool = OutpaintingImageGenerationTool(
    image_generation_driver=driver,
)

# Create an agent and provide the tool to it.
Agent(tools=[tool]).run(
    "Generate an image of a mountain shrouded by clouds by outpainting the "
    "image at tests/resources/mountain.png using the mask at tests/resources/mountain-mask.png."
)
