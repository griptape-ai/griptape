## Overview
Query engines are used to search collections of text.

## VectorQueryEngine

Used to query vector storages. You can set a custom [prompt_driver](../../reference/griptape/engines/query/vector_query_engine.md#griptape.engines.query.vector_query_engine.VectorQueryEngine.prompt_driver.md) and [vector_store_driver](../../reference/griptape/engines/query/vector_query_engine.md#griptape.engines.query.vector_query_engine.VectorQueryEngine.vector_store_driver.md). Uses [LocalVectorStoreDriver](../../reference/griptape/drivers/vector/local_vector_store_driver.md) by default.

Use the [upsert_text_artifact](../../reference/griptape/engines/query/vector_query_engine.md#griptape.engines.query.vector_query_engine.VectorQueryEngine.upsert_text_artifact.md) method to insert [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s into vector storage with an optional `namespace`.

Use the [VectorQueryEngine](../../reference/griptape/engines/query/vector_query_engine.md#griptape.engines.query.vector_query_engine.VectorQueryEngine.query.md) method to query the vector storage.

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
