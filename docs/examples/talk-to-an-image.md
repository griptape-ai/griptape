In this example, we use a [Local File Manager Driver](../griptape-framework/drivers/file-manager-drivers.md) to access the `images` directory in the current working directory.
We then pass this Driver to a [File Manager Tool](../griptape-framework/tools/official-tools/index.md#file-manager) and an [Image Query Tool](../griptape-framework/tools/official-tools/index.md#image-query) to interact with the images in the directory.

Note that if you update the `workdir` on a [File Manager Driver](../griptape-framework/drivers/file-manager-drivers.md), it's important to pass that Driver to all the Tools that need to access the same directory.

```python
--8<-- "docs/examples/src/talk_to_an_image_1.py"
```
