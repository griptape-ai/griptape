## Overview

[Image Generation Drivers](../../reference/griptape/drivers/image_generation/index.md) are used by [image generation Engines](../engines/image-generation-engines.md) to build and execute API calls to image generation models.

Provide a Driver when building an [Engine](../engines/image-generation-engines.md), then pass it to a [Tool](../tools/index.md) for use by an [Agent](../structures/agents.md):

```python
from griptape.structures import Agent
from griptape.engines import PromptImageGenerationEngine
from griptape.drivers import OpenAiImageGenerationDriver
from griptape.tools import PromptImageGenerationClient

driver = OpenAiImageGenerationDriver(
    model="dall-e-2",
)

engine = PromptImageGenerationEngine(image_generation_driver=driver)

agent = Agent(tools=[
    PromptImageGenerationClient(engine=engine),
])

agent.run("Generate a watercolor painting of a dog riding a skateboard")
```

### Amazon Bedrock

The [Amazon Bedrock Image Generation Driver](../../reference/griptape/drivers/image_generation/amazon_bedrock_image_generation_driver.md) provides multi-model access to image generation models hosted by Amazon Bedrock. This Driver manages API calls to the Bedrock API, while the specific Model Drivers below format the API requests and parse the responses.

#### Stable Diffusion

The [Bedrock Stable Diffusion Model Driver](../../reference/griptape/drivers/image_generation_model/bedrock_stable_diffusion_image_generation_model_driver.md) provides support for Stable Diffusion models hosted by Amazon Bedrock. This Model Driver supports configurations specific to Stable Diffusion, like style presets, clip guidance presets, and sampler.

This Model Driver supports negative prompts. When provided (for example, when used with an [image generation Engine](../engines/image-generation-engines.md) configured with [Negative Rulesets](../engines/image-generation-engines.md#image-generation-engine-rulesets)), the image generation request will include negatively-weighted prompts describing features or characteristics to avoid in the resulting generation.

```python
from griptape.structures import Agent
from griptape.tools import PromptImageGenerationClient
from griptape.engines import PromptImageGenerationEngine
from griptape.drivers import AmazonBedrockImageGenerationDriver, \
    BedrockStableDiffusionImageGenerationModelDriver

model_driver = BedrockStableDiffusionImageGenerationModelDriver(
    style_preset="pixel-art",
)

driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=model_driver,
    model="stability.stable-diffusion-xl-v0",
)

engine = PromptImageGenerationEngine(image_generation_driver=driver)

agent = Agent(tools=[
    PromptImageGenerationClient(engine=engine),
])

agent.run("Generate an image of a dog riding a skateboard")
```

#### Titan 

The [Bedrock Titan Image Generator Model Driver](../../reference/griptape/drivers/image_generation_model/bedrock_titan_image_generation_model_driver.md) provides support for Titan Image Generator models hosted by Amazon Bedrock. This Model Driver supports configurations specific to Titan Image Generator, like quality, seed, and cfg_scale.

This Model Driver supports negative prompts. When provided (for example, when used with an [image generation engine](../engines/image-generation-engines.md) configured with [Negative Rulesets](../engines/image-generation-engines.md#image-generation-engine-rulesets)), the image generation request will include negatively-weighted prompts describing features or characteristics to avoid in the resulting generation.

```python
from griptape.structures import Agent
from griptape.tools import PromptImageGenerationClient
from griptape.engines import PromptImageGenerationEngine
from griptape.drivers import AmazonBedrockImageGenerationDriver, \
    BedrockTitanImageGenerationModelDriver

model_driver = BedrockTitanImageGenerationModelDriver()

driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=model_driver,
    model="amazon.titan-image-generator-v1",
)

engine = PromptImageGenerationEngine(image_generation_driver=driver)

agent = Agent(tools=[
    PromptImageGenerationClient(engine=engine),
])

agent.run("Generate a watercolor painting of a dog riding a skateboard")
```

### Azure OpenAI

The [Azure OpenAI Image Generation Driver](../../reference/griptape/drivers/image_generation/azure_openai_image_generation_driver.md) provides access to OpenAI models hosted by Azure. In addition to the configurations provided by the underlying OpenAI Driver, the Azure OpenAI Driver allows configuration of Azure-specific deployment values.

```python
import os

from griptape.structures import Agent
from griptape.tools import PromptImageGenerationClient
from griptape.engines import PromptImageGenerationEngine
from griptape.drivers import AzureOpenAiImageGenerationDriver

driver = AzureOpenAiImageGenerationDriver(
    model="dall-e-3",
    azure_deployment=os.environ["AZURE_OPENAI_DALL_E_3_DEPLOYMENT_ID"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_2"],
    api_key=os.environ["AZURE_OPENAI_API_KEY_2"],
)

engine = PromptImageGenerationEngine(image_generation_driver=driver)

agent = Agent(tools=[
    PromptImageGenerationClient(engine=engine),
])

agent.run("Generate a watercolor painting of a dog riding a skateboard")
```

### Leonardo.Ai

The [Leonardo Image Generation Driver](../../reference/griptape/drivers/image_generation/leonardo_image_generation_driver.md) enables image generation using models hosted by [Leonardo.ai](https://leonardo.ai/).

This Driver supports configurations like model selection, image size, specifying a generation seed, and generation steps. For details on supported configuration parameters, see [Leonardo.Ai's image generation documentation](https://docs.leonardo.ai/reference/creategeneration).

This Driver supports negative prompts. When provided (for example, when used with an [image generation engine](../engines/image-generation-engines.md) configured with [Negative Rulesets](../engines/image-generation-engines.md#image-generation-engine-rulesets)), the image generation request will include negatively-weighted prompts describing features or characteristics to avoid in the resulting generation.

```python
import os

from griptape.structures import Agent
from griptape.tools import PromptImageGenerationClient
from griptape.engines import PromptImageGenerationEngine
from griptape.drivers import LeonardoImageGenerationDriver

driver = LeonardoImageGenerationDriver(
    model=os.environ["LEONARDO_MODEL_ID"],
    api_key=os.environ["LEONARDO_API_KEY"],
    image_width=512,
    image_height=1024,
)

engine = PromptImageGenerationEngine(image_generation_driver=driver)

agent = Agent(tools=[
    PromptImageGenerationClient(engine=engine),
])

agent.run("Generate a watercolor painting of a dog riding a skateboard")
```

### OpenAI

The [OpenAI Image Generation Driver](../../reference/griptape/drivers/image_generation/openai_image_generation_driver.md) provides access to OpenAI image generation models. Like other OpenAI Drivers, the image generation Driver will implicitly load an API key in the `OPENAI_API_KEY` environment variable if one is not explicitly provided.

This Driver supports image generation configurations like style presets, image quality preference, and image size. For details on supported configuration values, see the [OpenAI documentation](https://platform.openai.com/docs/guides/images/introduction).

```python
from griptape.structures import Agent
from griptape.tools import PromptImageGenerationClient
from griptape.engines import PromptImageGenerationEngine
from griptape.drivers import OpenAiImageGenerationDriver

driver = OpenAiImageGenerationDriver(
    model="dall-e-2",
    image_size="512x512",
)

engine = PromptImageGenerationEngine(image_generation_driver=driver)

agent = Agent(tools=[
    PromptImageGenerationClient(engine=engine),
])

agent.run("Generate a watercolor painting of a dog riding a skateboard")
```
