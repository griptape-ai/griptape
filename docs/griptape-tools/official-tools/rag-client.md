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
                response_module=PromptResponseRagModule(
                    prompt_driver=OpenAiChatPromptDriver(model="gpt-4o")
                )
            )
        )
)

agent = Agent(
    tools=[rag_client]
)

agent.run("what is Griptape?")

```
```
[07/11/24 08:47:04] INFO     ToolkitTask 4a5308b86cac447783e6abe1be0646cd       
                             Input: what is Griptape?                           
[07/11/24 08:47:06] INFO     Subtask e034a5d82658411694e9e19e51fa6699           
                             Thought: I need to search for information about    
                             Griptape using the RagClient. I will perform a     
                             search query to gather relevant details.           
                                                                                
                             Actions:                                           
                             [{"name":"RagClient","path":"search","input":{"valu
                             es":{"query":"What is                              
                             Griptape?"}},"tag":"search_griptape"}]             
[07/11/24 08:47:08] INFO     Subtask e034a5d82658411694e9e19e51fa6699           
                             Response: Griptape builds AI-powered applications  
                             that connect securely to your enterprise data and  
                             APIs. Griptape Agents provide incredible power and 
                             flexibility when working with large language       
                             models.                                            
[07/11/24 08:47:09] INFO     ToolkitTask 4a5308b86cac447783e6abe1be0646cd       
                             Output: Griptape builds AI-powered applications    
                             that connect securely to your enterprise data and  
                             APIs. Griptape Agents provide incredible power and 
                             flexibility when working with large language       
                             models.
```