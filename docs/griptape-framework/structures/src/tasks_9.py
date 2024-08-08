from griptape.artifacts import TextArtifact
from griptape.drivers import LocalVectorStoreDriver, OpenAiChatPromptDriver, OpenAiEmbeddingDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import PromptResponseRagModule, VectorStoreRetrievalRagModule
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage
from griptape.structures import Agent
from griptape.tasks import RagTask

# Initialize Embedding Driver and Vector Store Driver
vector_store_driver = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

artifacts = [
    TextArtifact("Griptape builds AI-powered applications that connect securely to your enterprise data and APIs."),
    TextArtifact("Griptape Agents provide incredible power and flexibility when working with large language models."),
]
vector_store_driver.upsert_text_artifacts({"griptape": artifacts})

# Instantiate the agent and add RagTask with the RagEngine
agent = Agent()
agent.add_task(
    RagTask(
        "Respond to the following query: {{ args[0] }}",
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
)

# Run the agent with a query string
agent.run("Give me information about Griptape")
