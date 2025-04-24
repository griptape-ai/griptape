from griptape.drivers.image_generation.amazon_bedrock import AmazonBedrockImageGenerationDriver
from griptape.drivers.image_generation_model.bedrock_stable_diffusion import (
    BedrockStableDiffusionImageGenerationModelDriver,
)
from griptape.structures import Agent
from griptape.tools import FileManagerTool, PromptImageGenerationTool, VariationImageGenerationTool

# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(
        style_preset="pixel-art",
    ),
    model="stability.stable-diffusion-xl-v1",
)

# Create a prompt image generation client configured to use the driver.
prompt_tool = PromptImageGenerationTool(image_generation_driver=driver, off_prompt=True)

# Create a variation image generation client configured to use the driver.
variation_tool = VariationImageGenerationTool(
    image_generation_driver=driver,
    off_prompt=True,
)

file_tool = FileManagerTool()

# Create an agent and provide the tools to it.
agent = Agent(tools=[prompt_tool, variation_tool, file_tool])

# Run the agent using a prompt motivating it to generate an image, then
# create a variation of the image present in task memory.
agent.run(
    "Generate an image of a mountain on a summer day. Then, generate a "
    "variation of this image depicting the same mountain scene on a winter day."
    "Save them images to disk and return the file paths. "
)
