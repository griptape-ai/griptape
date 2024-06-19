## Overview

[Image Generation Engines](../../reference/griptape/engines/image/index.md) facilitate text-to-image and image-to-image generation. Each Engine provides a `run` method that accepts the necessary inputs for its particular mode and provides the request to the configured [Driver](../drivers/image-generation-drivers.md).

### Image Generation Engine Rulesets

[Rulesets](../structures/rulesets.md) and Negative Rulesets are used by Engines to influence a model's output. Input rulesets are added to request prompts and can be used to standardize generated images across varying prompts. Negative rulesets are treated as negatively-weighted prompts and can be used to describe features or characteristics that should be avoided in the result.

In the following example, rulesets are provided to the Engine's `run()` method call. These rules are provided to the Driver and influence the model to generate an image in an artistic, watercolor style, while avoiding blurry, photographic characteristics.

!!! note "Not all Drivers support Negative Rulesets"
    See the [documentation for your Driver](../drivers/image-generation-drivers.md) to determine if it supports Negative Rulesets.

```python
from griptape.engines import PromptImageGenerationEngine
from griptape.drivers import AmazonBedrockImageGenerationDriver, \
    BedrockStableDiffusionImageGenerationModelDriver
from griptape.rules import Ruleset, Rule


# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(),
    model="stability.stable-diffusion-xl-v1",
)

# Create an engine configured to use the driver.
engine = PromptImageGenerationEngine(
    image_generation_driver=driver,
)

positive_ruleset = Ruleset(name="positive rules", rules=[Rule("artistic"), Rule("watercolor")])
negative_ruleset = Ruleset(name="negative rules", rules=[Rule("blurry"), Rule("photograph")])

engine.run(
    prompts=["A dog riding a skateboard"],
    rulesets=[positive_ruleset],
    negative_rulesets=[negative_ruleset],
)
```

### Prompt Image

This Engine facilitates generating images from text prompts.

```python
from griptape.engines import PromptImageGenerationEngine
from griptape.drivers import AmazonBedrockImageGenerationDriver, \
    BedrockStableDiffusionImageGenerationModelDriver


# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(),
    model="stability.stable-diffusion-xl-v1",
)

# Create an engine configured to use the driver.
engine = PromptImageGenerationEngine(
    image_generation_driver=driver,
)

engine.run(
    prompts=["A watercolor painting of a dog riding a skateboard"],
)
```

### Variation

This Engine facilitates generating variations of an input image according to a text prompt. The input image is used as a reference for the model's generation.

```python
from griptape.engines import VariationImageGenerationEngine
from griptape.drivers import AmazonBedrockImageGenerationDriver, \
    BedrockStableDiffusionImageGenerationModelDriver
from griptape.loaders import ImageLoader

# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(),
    model="stability.stable-diffusion-xl-v1",
)

# Create an engine configured to use the driver.
engine = VariationImageGenerationEngine(
    image_generation_driver=driver,
)

with open("tests/resources/mountain.png", "rb") as f:
    image_artifact = ImageLoader().load(f.read())
    
engine.run(
    prompts=["A photo of a mountain landscape in winter"],
    image=image_artifact,
)
```

### Inpainting

This Engine facilitates inpainting, or modifying an input image according to a text prompt within the bounds of a mask defined by mask image. After inpainting, the area specified by the mask is replaced with the model's generation, while the rest of the input image remains the same.

```python
from griptape.engines import InpaintingImageGenerationEngine
from griptape.drivers import AmazonBedrockImageGenerationDriver, \
    BedrockStableDiffusionImageGenerationModelDriver
from griptape.loaders import ImageLoader


# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(),
    model="stability.stable-diffusion-xl-v1",
)

# Create an engine configured to use the driver.
engine = InpaintingImageGenerationEngine(
    image_generation_driver=driver,
)

with open("tests/resources/mountain.png", "rb") as f:
    image_artifact = ImageLoader().load(f.read())
    
with open("tests/resources/mountain-mask.png", "rb") as f:
    mask_artifact = ImageLoader().load(f.read())
    
engine.run(
    prompts=["A photo of a castle built into the side of a mountain"],
    image=image_artifact,
    mask=mask_artifact,
)
```

### Outpainting

This Engine facilitates outpainting, or modifying an input image according to a text prompt outside the bounds of a mask defined by a mask image. After outpainting, the area of the input image specified by the mask remains the same, while the rest is replaced with the model's generation.

```python
from griptape.engines import OutpaintingImageGenerationEngine
from griptape.drivers import AmazonBedrockImageGenerationDriver, \
    BedrockStableDiffusionImageGenerationModelDriver
from griptape.loaders import ImageLoader

# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(),
    model="stability.stable-diffusion-xl-v1",
)

# Create an engine configured to use the driver.
engine = OutpaintingImageGenerationEngine(
    image_generation_driver=driver,
)

with open("tests/resources/mountain.png", "rb") as f:
    image_artifact = ImageLoader().load(f.read())
    
with open("tests/resources/mountain-mask.png", "rb") as f:
    mask_artifact = ImageLoader().load(f.read())
    
engine.run(
    prompts=["A photo of a mountain shrouded in clouds"],
    image=image_artifact,
    mask=mask_artifact,
)
```
