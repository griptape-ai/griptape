# InpaintingImageGenerationClient

This tool allows LLMs to generate images using inpainting, where an input image is altered within the area specified by a mask image according to a prompt. The input and mask images can be provided either by their file path or by their [Task Memory](../../griptape-framework/structures/task-memory.md) references.

```python
--8<-- "docs/griptape-tools/official-tools/src/inpainting_image_generation_client_1.py"
```
