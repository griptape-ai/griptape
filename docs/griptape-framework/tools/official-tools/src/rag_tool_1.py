from griptape.artifacts import TextArtifact
from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.drivers.vector.local import LocalVectorStoreDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import PromptResponseRagModule, VectorStoreRetrievalRagModule
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage
from griptape.structures import Agent
from griptape.tools import RagTool

vector_store_driver = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

artifact = TextArtifact(
    "Griptape builds AI-powered applications that connect securely to your enterprise data and APIs."
    "Griptape Agents provide incredible power and flexibility when working with large language models."
)

vector_store_driver.upsert(artifact, namespace="griptape")

rag_tool = RagTool(
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
            response_modules=[PromptResponseRagModule(prompt_driver=OpenAiChatPromptDriver(model="gpt-4.1"))]
        ),
    ),
)

agent = Agent(tools=[rag_tool])

agent.run("what is Griptape?")
