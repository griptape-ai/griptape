This example demonstrates how to vectorize a PDF of the [Attention Is All You Need](https://arxiv.org/pdf/1706.03762.pdf) paper and setup a Griptape agent with rules and the [VectorStoreClient](../reference/griptape/tools/vector_store_client/tool.md) tool to use it during conversations.

```python
import requests
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver, OpenAiChatPromptDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import VectorStoreRetrievalRagModule, PromptGenerationRagModule
from griptape.engines.rag.stages import RetrievalRagStage, GenerationRagStage
from griptape.loaders import PdfLoader
from griptape.structures import Agent
from griptape.tools import RagClient
from griptape.utils import Chat

namespace = "attention"
response = requests.get("https://arxiv.org/pdf/1706.03762.pdf")
vector_store = LocalVectorStoreDriver(
    embedding_driver=OpenAiEmbeddingDriver()
)
engine = RagEngine(
    retrieval_stage=RetrievalRagStage(
        retrieval_modules=[
            VectorStoreRetrievalRagModule(
                namespace=namespace,
                vector_store_driver=vector_store,
                top_n=20
            )
        ]
    ),
    generation_stage=GenerationRagStage(
        generation_module=PromptGenerationRagModule(
            prompt_driver=OpenAiChatPromptDriver(model="gpt-4o")
        )
    )
)
vector_store_tool = RagClient(
    description="Contains information about the Attention Is All You Need paper. "
                "Use it to answer any related questions.",
    rag_engine=engine
)

vector_store.upsert_text_artifacts(
    {
        namespace: PdfLoader().load(response.content)
    }
)

agent = Agent(
    tools=[vector_store_tool]
)

Chat(agent).start()

```
