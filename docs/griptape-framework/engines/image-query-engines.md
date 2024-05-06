# ImageQueryEngine

The [Image Query Engine](../../reference/griptape/engines/image_query/image_query_engine.md) is used to execute natural language queries on the contents of images. You can specify the provider and model used to query the image by providing the Engine with a particular [Image Query Driver](../drivers/image-query-drivers.md).

All Image Query Drivers default to a `max_tokens` of 256. You can tune this value based on your use case and the [Image Query Driver](../drivers/image-query-drivers.md) you are providing. 

```python
from griptape.drivers import OpenAiVisionImageQueryDriver
from griptape.engines import ImageQueryEngine
from griptape.loaders import ImageLoader

driver = OpenAiVisionImageQueryDriver(
    model="gpt-4-vision-preview",
    max_tokens=256
)

engine = ImageQueryEngine(
    image_query_driver=driver
)

with open("tests/resources/mountain.png", "rb") as f:
    image_artifact = ImageLoader().load(f.read())

engine.run("Describe the weather in the image", [image_artifact])
```
