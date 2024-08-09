from griptape.drivers import AmazonBedrockImageGenerationDriver, BedrockStableDiffusionImageGenerationModelDriver
from griptape.engines import PromptImageGenerationEngine, VariationImageGenerationEngine
from griptape.structures import Agent
from griptape.tools import PromptImageGenerationClient, VariationImageGenerationClient

# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(
        style_preset="pixel-art",
    ),
    model="stability.stable-diffusion-xl-v0",
)

# Create an prompt image generation engine configured to use the driver.
prompt_engine = PromptImageGenerationEngine(
    image_generation_driver=driver,
)

# Create a prompt image generation client configured to use the engine.
prompt_tool = PromptImageGenerationClient(
    engine=prompt_engine,
)

# Create an variation image generation engine configured to use the driver.
variation_engine = VariationImageGenerationEngine(
    image_generation_driver=driver,
)

# Create a variation image generation client configured to use the engine.
variation_tool = VariationImageGenerationClient(
    engine=variation_engine,
)

# Create an agent and provide the tools to it.
agent = Agent(tools=[prompt_tool, variation_tool])

# Run the agent using a prompt motivating it to generate an image, then
# create a variation of the image present in task memory.
agent.run(
    "Generate an image of a mountain on a summer day. Then, generate a "
    "variation of this image depicting the same mountain scene on a winter day."
)
