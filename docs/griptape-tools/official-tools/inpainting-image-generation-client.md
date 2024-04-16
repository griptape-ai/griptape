# InpaintingImageGenerationClient

This tool allows LLMs to generate images using inpainting, where an input image is altered within the area specified by a mask image according to a prompt. The input and mask images can be provided either by their file path or by their [Task Memory](../../griptape-framework/structures/task-memory.md) references.

```python
from griptape.structures import Agent
from griptape.engines import InpaintingImageGenerationEngine
from griptape.drivers import AmazonBedrockImageGenerationDriver, \
    BedrockStableDiffusionImageGenerationModelDriver
from griptape.tools import InpaintingImageGenerationClient


# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(),
    model="stability.stable-diffusion-xl-v0",
)

# Create an engine configured to use the driver.
engine = InpaintingImageGenerationEngine(
    image_generation_driver=driver,
)

# Create a tool configured to use the engine.
tool = InpaintingImageGenerationClient(
    engine=engine,
)

# Create an agent and provide the tool to it.
Agent(tools=[tool]).run("Generate an image of a castle built into the side of a mountain by inpainting the "
                        "image at tests/resources/mountain.png using the mask at tests/resources/mountain-mask.png.")
```
