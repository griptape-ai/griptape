## Overview
Query engines are used to perform text queries against various modalities. 

## Vector

Used to query vector storages. You can set a custom [prompt_driver](../../reference/griptape/engines/query/vector_query_engine.md#griptape.engines.query.vector_query_engine.VectorQueryEngine.prompt_driver) and [vector_store_driver](../../reference/griptape/engines/query/vector_query_engine.md#griptape.engines.query.vector_query_engine.VectorQueryEngine.vector_store_driver). Uses [LocalVectorStoreDriver](../../reference/griptape/drivers/vector/local_vector_store_driver.md) by default.

Use the [upsert_text_artifact](../../reference/griptape/engines/query/vector_query_engine.md#griptape.engines.query.vector_query_engine.VectorQueryEngine.upsert_text_artifact)s into vector storage with an optional `namespace`.

Use the [VectorQueryEngine](../../reference/griptape/engines/query/vector_query_engine.md#griptape.engines.query.vector_query_engine.VectorQueryEngine.query) method to query the vector storage.

```python
from griptape.drivers import OpenAiChatPromptDriver, LocalVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.engines import VectorQueryEngine
from griptape.loaders import WebLoader

engine = VectorQueryEngine(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"),
    vector_store_driver=LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())
)

engine.upsert_text_artifacts(
    WebLoader().load("https://www.griptape.ai"), namespace="griptape"
)

engine.query("what is griptape?", namespace="griptape")
```

## Image
The [Image Query Engine](../../reference/griptape/engines/image_query/image_query_engine.md) allows you to perform natural language queries on the contents of images. You can specify the provider and model used to query the image by providing the Engine with a particular [Image Query Driver](../drivers/image-query-drivers.md).

All Image Query Drivers default to a `max_tokens` of 256. You can tune this value based on your use case and the [Image Query Driver](../drivers/image-query-drivers.md) you are providing.

```python
from griptape.drivers import OpenAiImageQueryDriver
from griptape.engines import ImageQueryEngine
from griptape.loaders import ImageLoader

driver = OpenAiImageQueryDriver(
    model="gpt-4o",
    max_tokens=256
)

engine = ImageQueryEngine(
    image_query_driver=driver
)

with open("tests/resources/mountain.png", "rb") as f:
    image_artifact = ImageLoader().load(f.read())

engine.run("Describe the weather in the image", [image_artifact])
```
