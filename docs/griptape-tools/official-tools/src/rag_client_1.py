from griptape.artifacts import TextArtifact
from griptape.drivers import LocalVectorStoreDriver, OpenAiChatPromptDriver, OpenAiEmbeddingDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import PromptResponseRagModule, VectorStoreRetrievalRagModule
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage
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
                    vector_store_driver=vector_store_driver, query_params={"namespace": "griptape", "top_n": 20}
                )
            ]
        ),
        response_stage=ResponseRagStage(
            response_module=PromptResponseRagModule(prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"))
        ),
    ),
)

agent = Agent(tools=[rag_client])

agent.run("what is Griptape?")
