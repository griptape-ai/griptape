from griptape.drivers import AmazonBedrockImageGenerationDriver, BedrockStableDiffusionImageGenerationModelDriver
from griptape.engines import OutpaintingImageGenerationEngine
from griptape.structures import Agent
from griptape.tools import OutpaintingImageGenerationClient

# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(),
    model="stability.stable-diffusion-xl-v0",
)

# Create an engine configured to use the driver.
engine = OutpaintingImageGenerationEngine(
    image_generation_driver=driver,
)

# Create a tool configured to use the engine.
tool = OutpaintingImageGenerationClient(
    engine=engine,
)

# Create an agent and provide the tool to it.
Agent(tools=[tool]).run(
    "Generate an image of a mountain shrouded by clouds by outpainting the "
    "image at tests/resources/mountain.png using the mask at tests/resources/mountain-mask.png."
)
