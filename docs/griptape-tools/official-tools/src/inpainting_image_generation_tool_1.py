from griptape.drivers import AmazonBedrockImageGenerationDriver, BedrockStableDiffusionImageGenerationModelDriver
from griptape.structures import Agent
from griptape.tools import InpaintingImageGenerationTool

# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(),
    model="stability.stable-diffusion-xl-v0",
)

# Create a tool configured to use the engine.
tool = InpaintingImageGenerationTool(
    image_generation_driver=driver,
)

# Create an agent and provide the tool to it.
Agent(tools=[tool]).run(
    "Generate an image of a castle built into the side of a mountain by inpainting the "
    "image at tests/resources/mountain.png using the mask at tests/resources/mountain-mask.png."
)
