The [VectorStoreClient](../../reference/griptape/tools/vector_store_client/tool.md) enables LLMs to dynamically query task memory.

Here is an example of how it can be used with the Pincone storage driver:

```python
from griptape.structures import Agent
from griptape.tools import VectorStoreClient, TaskMemoryClient
from griptape.loaders import WebLoader
from griptape.engines import VectorQueryEngine
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver, OpenAiChatPromptDriver

engine = VectorQueryEngine(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"),
    vector_store_driver=LocalVectorStoreDriver(
        embedding_driver=OpenAiEmbeddingDriver(),
    ),
)

engine.upsert_text_artifacts(
    WebLoader().load("https://www.griptape.ai"),
    namespace="griptape"
)
    
vector_db = VectorStoreClient(
    description="This DB has information about the Griptape Python framework",
    query_engine=engine,
    namespace="griptape",
    off_prompt=True
)

agent = Agent(
    tools=[vector_db, TaskMemoryClient(off_prompt=False)]
)

agent.run(
    "what is Griptape?"
)
```
