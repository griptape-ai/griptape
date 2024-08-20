---
search:
  boost: 2 
---

## Overview

[Image Generation Engines](../../reference/griptape/engines/image/index.md) facilitate text-to-image and image-to-image generation. Each Engine provides a `run` method that accepts the necessary inputs for its particular mode and provides the request to the configured [Driver](../drivers/image-generation-drivers.md).

### Image Generation Engine Rulesets

[Rulesets](../structures/rulesets.md) and Negative Rulesets are used by Engines to influence a model's output. Input rulesets are added to request prompts and can be used to standardize generated images across varying prompts. Negative rulesets are treated as negatively-weighted prompts and can be used to describe features or characteristics that should be avoided in the result.

In the following example, rulesets are provided to the Engine's `run()` method call. These rules are provided to the Driver and influence the model to generate an image in an artistic, watercolor style, while avoiding blurry, photographic characteristics.

!!! note "Not all Drivers support Negative Rulesets"
    See the [documentation for your Driver](../drivers/image-generation-drivers.md) to determine if it supports Negative Rulesets.

```python
--8<-- "docs/griptape-framework/engines/src/image_generation_engines_1.py"
```

### Prompt Image

This Engine facilitates generating images from text prompts.

```python
--8<-- "docs/griptape-framework/engines/src/image_generation_engines_2.py"
```

### Variation

This Engine facilitates generating variations of an input image according to a text prompt. The input image is used as a reference for the model's generation.

```python
--8<-- "docs/griptape-framework/engines/src/image_generation_engines_3.py"
```

### Inpainting

This Engine facilitates inpainting, or modifying an input image according to a text prompt within the bounds of a mask defined by mask image. After inpainting, the area specified by the mask is replaced with the model's generation, while the rest of the input image remains the same.

```python
--8<-- "docs/griptape-framework/engines/src/image_generation_engines_4.py"
```

### Outpainting

This Engine facilitates outpainting, or modifying an input image according to a text prompt outside the bounds of a mask defined by a mask image. After outpainting, the area of the input image specified by the mask remains the same, while the rest is replaced with the model's generation.

```python
--8<-- "docs/griptape-framework/engines/src/image_generation_engines_5.py"
```
