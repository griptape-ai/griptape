The following example script ingests a Web page (a blog post),
stores its chunked contents on Astra DB through the Astra DB vector store driver,
and finally runs a RAG process to answer a question specific to the topic of the
Web page.

This script requires that a vector collection has been created in the Astra database
(with name `"griptape_test_collection"` and vector dimension matching the embedding being used, i.e. 1536 in this case).

_Note:_ Besides the [Astra DB](../griptape-framework/drivers/vector-store-drivers.md#astra-db) extra,
this example requires the `drivers-web-scraper-trafilatura`
Griptape extra to be installed as well.


```python
import os

from griptape.drivers import (
    AstraDbVectorStoreDriver,
    OpenAiChatPromptDriver,
    OpenAiEmbeddingDriver,
)
from griptape.engines import PromptEngine
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import (
    PromptResponseRagModule,
    VectorStoreRetrievalRagModule,
)
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage
from griptape.loaders import WebLoader
from griptape.structures import Agent
from griptape.tools import RagClient, TaskMemoryClient


namespace = "datastax_blog"
input_blogpost = (
    "www.datastax.com/blog/indexing-all-of-wikipedia-on-a-laptop"
)

vector_store_driver = AstraDbVectorStoreDriver(
    embedding_driver=OpenAiEmbeddingDriver(),
    api_endpoint=os.environ["ASTRA_DB_API_ENDPOINT"],
    token=os.environ["ASTRA_DB_APPLICATION_TOKEN"],
    collection_name="griptape_test_collection",
    astra_db_namespace=os.environ.get("ASTRA_DB_KEYSPACE"),
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
            prompt_engine=PromptEngine(
                prompt_driver=OpenAiChatPromptDriver(model="gpt-4o")
            )
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
