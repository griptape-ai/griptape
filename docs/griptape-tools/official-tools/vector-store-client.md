The [VectorStoreClient](../../reference/griptape/tools/vector_store_client/tool.md) enables LLMs to query vector stores.

Here is an example of how it can be used with a local vector store driver:

```python
from griptape.structures import Agent
from griptape.tools import VectorStoreClient, TaskMemoryClient
from griptape.loaders import WebLoader
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver

vector_store_driver = LocalVectorStoreDriver(
    embedding_driver=OpenAiEmbeddingDriver(),
)

vector_store_driver.upsert_text_artifacts(
    {
        "griptape": WebLoader().load("https://www.griptape.ai")
    }
)
    
vector_db = VectorStoreClient(
    description="This DB has information about the Griptape Python framework",
    vector_store_driver=vector_store_driver,
    query_params={"namespace": "griptape"},
    off_prompt=True
)

agent = Agent(
    tools=[vector_db, TaskMemoryClient(off_prompt=False)]
)

agent.run(
    "what is Griptape?"
)
```
