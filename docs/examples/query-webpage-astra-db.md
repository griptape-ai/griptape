Required Griptape extras:

```
pip install griptape[drivers-vector-astra-db,drivers-web-scraper-trafilatura]
```

Python script:

```python
import os

from griptape.drivers import (
    AstraDBVectorStoreDriver,
    OpenAiChatPromptDriver,
    OpenAiEmbeddingDriver,
)
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import (
    PromptResponseRagModule,
    VectorStoreRetrievalRagModule,
)
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage
from griptape.loaders import WebLoader
from griptape.structures import Agent
from griptape.tools import RagClient, TaskMemoryClient

if __name__ == "__main__":
    namespace = "datastax_blog"
    input_blogpost = (
        "www.datastax.com/blog/indexing-all-of-wikipedia-on-a-laptop"
    )

    vector_store_driver = AstraDBVectorStoreDriver(
        embedding_driver=OpenAiEmbeddingDriver(),
        api_endpoint=os.environ["ASTRA_DB_API_ENDPOINT"],
        token=os.environ["ASTRA_DB_APPLICATION_TOKEN"],
        collection_name="griptape_test_collection",
        astra_db_namespace=os.environ.get("ASTRA_DB_KEYSPACE"),
        dimension=1536,
    )

    engine = RagEngine(
        retrieval_stage=RetrievalRagStage(
            retrieval_modules=[
                VectorStoreRetrievalRagModule(
                    vector_store_driver=vector_store_driver,
                    query_params={
                        "count": 2,
                        "namespace": namespace,
                    },
                )
            ]
        ),
        response_stage=ResponseRagStage(
            response_module=PromptResponseRagModule(
                prompt_driver=OpenAiChatPromptDriver(model="gpt-4o")
            )
        )
    )

    vector_store_driver.upsert_text_artifacts(
        {namespace: WebLoader(max_tokens=256).load(input_blogpost)}
    )

    vector_store_tool = RagClient(
        description="A DataStax blog post",
        rag_engine=engine,
    )
    agent = Agent(tools=[vector_store_tool, TaskMemoryClient(off_prompt=False)])
    agent.run(
        "What engine made possible to index such an amount of data, "
        "and what kind of tuning was required?"
    )
```
