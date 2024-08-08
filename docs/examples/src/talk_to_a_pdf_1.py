import requests

from griptape.drivers import LocalVectorStoreDriver, OpenAiChatPromptDriver, OpenAiEmbeddingDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import PromptResponseRagModule, VectorStoreRetrievalRagModule
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage
from griptape.loaders import PdfLoader
from griptape.structures import Agent
from griptape.tools import RagClient
from griptape.utils import Chat

namespace = "attention"
response = requests.get("https://arxiv.org/pdf/1706.03762.pdf")
vector_store = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())
engine = RagEngine(
    retrieval_stage=RetrievalRagStage(
        retrieval_modules=[
            VectorStoreRetrievalRagModule(
                vector_store_driver=vector_store, query_params={"namespace": namespace, "top_n": 20}
            )
        ]
    ),
    response_stage=ResponseRagStage(
        response_module=PromptResponseRagModule(prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"))
    ),
)
vector_store_tool = RagClient(
    description="Contains information about the Attention Is All You Need paper. "
    "Use it to answer any related questions.",
    rag_engine=engine,
)

vector_store.upsert_text_artifacts({namespace: PdfLoader().load(response.content)})

agent = Agent(tools=[vector_store_tool])

Chat(agent).start()
