The [RagClient](../../reference/griptape/tools/rag_client/tool.md) enables LLMs to query modular RAG engines.

Here is an example of how it can be used with a local vector store driver:

```python
from griptape.artifacts import TextArtifact
from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver, OpenAiChatPromptDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import VectorStoreRetrievalRagModule, PromptResponseRagModule
from griptape.engines.rag.stages import RetrievalRagStage, ResponseRagStage
from griptape.structures import Agent
from griptape.tools import RagClient


vector_store_driver = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

artifact = TextArtifact(
    "Griptape builds AI-powered applications that connect securely to your enterprise data and APIs."
    "Griptape Agents provide incredible power and flexibility when working with large language models."
)

vector_store_driver.upsert_text_artifact(artifact=artifact, namespace="griptape")

rag_client = RagClient(
    description="Contains information about Griptape",
    off_prompt=False,
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
                response_modules=[
                    PromptResponseRagModule(
                        prompt_driver=OpenAiChatPromptDriver(model="gpt-4o")
                    )
                ]
            )
        )
)

agent = Agent(
    tools=[rag_client]
)

agent.run("what is Griptape?")

```
```
[07/11/24 13:30:43] INFO     ToolkitTask a6d057d5c71d4e9cb6863a2adb64b76c
                             Input: what is Griptape?
[07/11/24 13:30:44] INFO     Subtask 8fd89ed9eefe49b8892187f2fca3890a
                             Actions: [
                               {
                                 "tag": "call_4MaDzOuKnWAs2gmhK3KJhtjI",
                                 "name": "RagClient",
                                 "path": "search",
                                 "input": {
                                   "values": {
                                     "query": "What is Griptape?"
                                   }
                                 }
                               }
                             ]
[07/11/24 13:30:49] INFO     Subtask 8fd89ed9eefe49b8892187f2fca3890a
                             Response: Griptape builds AI-powered applications that connect securely to your enterprise data and APIs. Griptape Agents provide incredible
                             power and flexibility when working with large language models.
                    INFO     ToolkitTask a6d057d5c71d4e9cb6863a2adb64b76c
                             Output: Griptape builds AI-powered applications that connect securely to your enterprise data and APIs. Griptape Agents provide incredible
                             power and flexibility when working with large language models.
```
