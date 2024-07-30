---
search:
  boost: 2 
---

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

## Image Generation Drivers

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

### HuggingFace Pipelines

!!! info
    This driver requires the `drivers-image-generation-huggingface` [extra](../index.md#extras).

The [HuggingFace Pipelines Image Generation Driver](../../reference/griptape/drivers/image_generation/huggingface_pipeline_image_generation_driver.md) enables image generation through locally-hosted models using the HuggingFace [Diffusers](https://huggingface.co/docs/diffusers/en/index) library. This Driver requires a [Pipeline Driver](../../reference/griptape/drivers/image_generation_pipeline/index.md) to prepare the appropriate Pipeline.

This Driver requires a `model` configuration, specifying the model to use for image generation. The value of the `model` configuration must be one of the following:

 - A model name from the HuggingFace Model Hub, like `stabilityai/stable-diffusion-3-medium-diffusers`
 - A path to the directory containing a model on the filesystem, like `./models/stable-diffusion-3/`
 - A path to a file containing a model on the filesystem, like `./models/sd3_medium_incl_clips.safetensors`

The `device` configuration specifies the hardware device used to run inference. Common values include `cuda` (supporting CUDA-enabled GPUs), `cpu` (supported by a device's CPU), and `mps` (supported by Apple silicon GPUs). For more information, see [HuggingFace's documentation](https://huggingface.co/docs/transformers/en/perf_infer_gpu_one) on GPU inference.

#### Stable Diffusion 3 Image Generation Pipeline Driver

!!! info
    The `Stable Diffusion 3 Image Generation Pipeline Driver` requires the `drivers-image-generation-huggingface` extra.

The [Stable Diffusion 3 Image Generation Pipeline Driver](../../reference/griptape/drivers/image_generation_pipeline/stable_diffusion_3_image_generation_pipeline_driver.md) provides a Stable `Diffusion3DiffusionPipeline` for text-to-image generations via the [HuggingFace Pipelines Image Generation Driver's](../../reference/griptape/drivers/image_generation/huggingface_pipeline_image_generation_driver.md) `.try_text_to_image()` method. This Driver accepts a text prompt and configurations including Stable Diffusion 3 model, output image size, generation seed, and inference steps.

Image generation consumes substantial memory. On devices with limited VRAM, it may be necessary to enable the `enable_model_cpu_offload` or `drop_t5_encoder` configurations. For more information, see [HuggingFace's documentation](https://huggingface.co/docs/diffusers/en/optimization/memory) on reduced memory usage.

```python title="PYTEST_IGNORE"
from griptape.structures import Pipeline
from griptape.tasks import PromptImageGenerationTask
from griptape.engines import PromptImageGenerationEngine
from griptape.drivers import HuggingFacePipelineImageGenerationDriver, \
    StableDiffusion3ImageGenerationPipelineDriver
from griptape.artifacts import TextArtifact

image_generation_task = PromptImageGenerationTask(
    input=TextArtifact("landscape photograph, verdant, countryside, 8k"),
    image_generation_engine=PromptImageGenerationEngine(
        image_generation_driver=HuggingFacePipelineImageGenerationDriver(
            model="stabilityai/stable-diffusion-3-medium-diffusers",
            device="cuda",
            pipeline_driver=StableDiffusion3ImageGenerationPipelineDriver(
                height=512,
                width=512,
            )
        )
    )
)

output_artifact = Pipeline(tasks=[image_generation_task]).run().output
```

#### Stable Diffusion 3 Img2Img Image Generation Pipeline Driver

!!! info
    The `Stable Diffusion 3 Image Generation Pipeline Driver` requires the `drivers-image-generation-huggingface` extra.

The [Stable Diffusion 3 Img2Img Image Generation Pipeline Driver](../../reference/griptape/drivers/image_generation_pipeline/stable_diffusion_3_img_2_img_image_generation_pipeline_driver.md) provides a `StableDiffusion3Img2ImgPipeline` for image-to-image generations, accepting a text prompt and input image. This Driver accepts a text prompt, an input image, and configurations including Stable Diffusion 3 model, output image size, inference steps, generation seed, and strength of generation over the input image.

```python title="PYTEST_IGNORE"
from pathlib import Path

from griptape.structures import Pipeline
from griptape.tasks import VariationImageGenerationTask
from griptape.engines import VariationImageGenerationEngine
from griptape.drivers import HuggingFacePipelineImageGenerationDriver, \
    StableDiffusion3Img2ImgImageGenerationPipelineDriver
from griptape.artifacts import TextArtifact, ImageArtifact
from griptape.loaders import ImageLoader

prompt_artifact = TextArtifact("landscape photograph, verdant, countryside, 8k")
input_image_artifact = ImageLoader().load(Path("tests/resources/mountain.png").read_bytes())

image_variation_task = VariationImageGenerationTask(
    input=(prompt_artifact, input_image_artifact),
    image_generation_engine=PromptImageGenerationEngine(
        image_generation_driver=HuggingFacePipelineImageGenerationDriver(
            model="stabilityai/stable-diffusion-3-medium-diffusers",
            device="cuda",
            pipeline_driver=StableDiffusion3Img2ImgImageGenerationPipelineDriver(
                height=1024,
                width=1024,
            )
        )
    )
)

output_artifact = Pipeline(tasks=[image_variation_task]).run().output
```

#### StableDiffusion3ControlNetImageGenerationPipelineDriver

!!! note
    The `Stable Diffusion 3 Image Generation Pipeline Driver` requires the `drivers-image-generation-huggingface` extra.

The [StableDiffusion3ControlNetImageGenerationPipelineDriver](../../reference/griptape/drivers/image_generation_pipeline/stable_diffusion_3_controlnet_image_generation_pipeline_driver.md) provides a `StableDiffusion3ControlNetPipeline` for image-to-image generations, accepting a text prompt and a control image. This Driver accepts a text prompt, a control image, and configurations including Stable Diffusion 3 model, ControlNet model, output image size, generation seed, inference steps, and the degree to which the model adheres to the control image.

```python title="PYTEST_IGNORE"
from pathlib import Path

from griptape.structures import Pipeline
from griptape.tasks import VariationImageGenerationTask
from griptape.engines import VariationImageGenerationEngine
from griptape.drivers import HuggingFacePipelineImageGenerationDriver, \
    StableDiffusion3ControlNetImageGenerationPipelineDriver
from griptape.artifacts import TextArtifact, ImageArtifact
from griptape.loaders import ImageLoader

prompt_artifact = TextArtifact("landscape photograph, verdant, countryside, 8k")
control_image_artifact = ImageLoader().load(Path("canny_control_image.png").read_bytes())

controlnet_task = VariationImageGenerationTask(
    input=(prompt_artifact, control_image_artifact),
    image_generation_engine=PromptImageGenerationEngine(
        image_generation_driver=HuggingFacePipelineImageGenerationDriver(
            model="stabilityai/stable-diffusion-3-medium-diffusers",
            device="cuda",
            pipeline_driver=StableDiffusion3ControlNetImageGenerationPipelineDriver(
                controlnet_model="InstantX/SD3-Controlnet-Canny",
                control_strength=0.8,
                height=768,
                width=1024,
            )
        )
    )
)

output_artifact = Pipeline(tasks=[controlnet_task]).run().output
```
