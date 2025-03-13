import os

from griptape.chunkers import TextChunker
from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.drivers.vector.astradb import AstraDbVectorStoreDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import (
    PromptResponseRagModule,
    VectorStoreRetrievalRagModule,
)
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage
from griptape.loaders import WebLoader
from griptape.structures import Agent
from griptape.tools import RagTool

namespace = "datastax_blog"
input_blogpost = "www.datastax.com/blog/indexing-all-of-wikipedia-on-a-laptop"

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
        response_modules=[PromptResponseRagModule(prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"))]
    ),
)

artifacts = WebLoader().load(input_blogpost)
chunks = TextChunker(max_tokens=256).chunk(artifacts)
vector_store_driver.upsert_collection({namespace: chunks})

rag_tool = RagTool(
    description="A DataStax blog post",
    rag_engine=engine,
)
agent = Agent(tools=[rag_tool])
agent.run("What engine made possible to index such an amount of data, and what kind of tuning was required?")
