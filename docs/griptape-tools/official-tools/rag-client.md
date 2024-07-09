The [RagClient](../../reference/griptape/tools/rag_client/tool.md) enables LLMs to query modular RAG engines.

Here is an example of how it can be used with a local vector store driver:

```python
from griptape.structures import Agent
from griptape.tasks import RagTask
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver, OpenAiChatPromptDriver
from griptape.artifacts import TextArtifact
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import VectorStoreRetrievalRagModule, PromptResponseRagModule
from griptape.engines.rag.stages import RetrievalRagStage, ResponseRagStage

# Initialize Embedding Driver and Vector Store Driver
vector_store_driver = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

artifact = TextArtifact(
    "Griptape builds AI-powered applications that connect securely to your enterprise data and APIs."
    "Griptape Agents provide incredible power and flexibility when working with large language models."
)
vector_store_driver.upsert_text_artifact(artifact=artifact, namespace="griptape")

# Instantiate the agent and add RagTask with the RagEngine
agent = Agent()
agent.add_task(
    RagTask(
        "Respond to the following query: {{ args[0] }}",
        rag_engine=RagEngine(
            retrieval_stage=RetrievalRagStage(
                retrieval_modules=[
                    VectorStoreRetrievalRagModule(
                        vector_store_driver=vector_store_driver,
                        query_params={
                            "namespace": "griptape",
                            "top_n": 20
                        }
                    )
                ]
            ),
            response_stage=ResponseRagStage(
                response_module=PromptResponseRagModule(
                    prompt_driver=OpenAiChatPromptDriver(model="gpt-4o")
                )
            )
        ),
    )
)

# Run the agent with a query string
agent.run("Give me information about Griptape")
```
