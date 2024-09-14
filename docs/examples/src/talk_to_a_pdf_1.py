import requests

from griptape.drivers import LocalVectorStoreDriver, OpenAiChatPromptDriver, OpenAiEmbeddingDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import PromptResponseRagModule, VectorStoreRetrievalRagModule
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage
from griptape.loaders import PdfLoader
from griptape.structures import Agent
from griptape.tools import RagTool
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
        response_modules=[PromptResponseRagModule(prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"))]
    ),
)
rag_tool = RagTool(
    description="Contains information about the Attention Is All You Need paper. "
    "Use it to answer any related questions.",
    rag_engine=engine,
)

artifacts = PdfLoader().load(response.content)

vector_store.upsert_text_artifacts({namespace: artifacts})

agent = Agent(tools=[rag_tool])

Chat(agent).start()
