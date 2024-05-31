# VariationImageGenerationEngine

This Tool allows LLMs to generate variations of an input image from a text prompt. The input image can be provided either by its file path or by its [Task Memory](../../griptape-framework/structures/task-memory.md) reference. 

## Referencing an Image by File Path

```python
from griptape.structures import Agent
from griptape.engines import VariationImageGenerationEngine
from griptape.drivers import AmazonBedrockImageGenerationDriver, \
    BedrockStableDiffusionImageGenerationModelDriver
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
Agent(tools=[tool]).run("Generate a variation of the image located at tests/resources/mountain.png " 
                        "depicting a mountain on a winter day")
```

## Referencing an Image in Task Memory

```python
from griptape.structures import Agent
from griptape.engines import VariationImageGenerationEngine, PromptImageGenerationEngine
from griptape.drivers import AmazonBedrockImageGenerationDriver, \
    BedrockStableDiffusionImageGenerationModelDriver
from griptape.tools import VariationImageGenerationClient, PromptImageGenerationClient


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
agent.run("Generate an image of a mountain on a summer day. Then, generate a "
          "variation of this image depicting the same mountain scene on a winter day.")          
```
