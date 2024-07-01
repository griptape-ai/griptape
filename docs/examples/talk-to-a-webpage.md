This example demonstrates how to vectorize a webpage and setup a Griptape agent with rules and the [RagClient](../reference/griptape/tools/rag_client/tool.md) tool to use it during conversations.

```python
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver, OpenAiChatPromptDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import VectorStoreRetrievalRagModule, PromptGenerationRagModule
from griptape.engines.rag.stages import RetrievalRagStage, ResponseRagStage
from griptape.loaders import WebLoader
from griptape.rules import Ruleset, Rule
from griptape.structures import Agent
from griptape.tools import RagClient
from griptape.utils import Chat

namespace = "physics-wiki"

vector_store_driver = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

engine = RagEngine(
    retrieval_stage=RetrievalRagStage(
        retrieval_modules=[
            VectorStoreRetrievalRagModule(
                namespace=namespace,
                vector_store_driver=vector_store_driver,
                top_n=20
            )
        ]
    ),
    response_stage=ResponseRagStage(
        generation_module=PromptGenerationRagModule(
            prompt_driver=OpenAiChatPromptDriver(model="gpt-4o")
        )
    )
)

artifacts = WebLoader().load(
    "https://en.wikipedia.org/wiki/Physics"
)

vector_store_driver.upsert_text_artifacts(
    {namespace: artifacts}
)

vector_store_tool = RagClient(
    description="Contains information about physics. "
                "Use it to answer any physics-related questions.",
    rag_engine=engine
)

agent = Agent(
    rulesets=[
        Ruleset(
            name="Physics Tutor",
            rules=[
                Rule(
                    "Always introduce yourself as a physics tutor"
                ),
                Rule(
                    "Be truthful. Only discuss physics."
                )
            ]
        )
    ],
    tools=[vector_store_tool]
)

Chat(agent).start()
```
