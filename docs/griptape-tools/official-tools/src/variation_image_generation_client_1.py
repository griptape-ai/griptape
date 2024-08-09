from griptape.drivers import AmazonBedrockImageGenerationDriver, BedrockStableDiffusionImageGenerationModelDriver
from griptape.engines import VariationImageGenerationEngine
from griptape.structures import Agent
from griptape.tools import VariationImageGenerationClient

# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(
        style_preset="pixel-art",
    ),
    model="stability.stable-diffusion-xl-v0",
)

# Create an engine configured to use the driver.
engine = VariationImageGenerationEngine(
    image_generation_driver=driver,
)

# Create a tool configured to use the engine.
tool = VariationImageGenerationClient(
    engine=engine,
)

# Create an agent and provide the tool to it.
Agent(tools=[tool]).run(
    "Generate a variation of the image located at tests/resources/mountain.png " "depicting a mountain on a winter day"
)
