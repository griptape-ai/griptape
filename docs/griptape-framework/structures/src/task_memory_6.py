from griptape.artifacts import TextArtifact
from griptape.config import (
    OpenAiStructureConfig,
)
from griptape.drivers import (
    LocalVectorStoreDriver,
    OpenAiChatPromptDriver,
    OpenAiEmbeddingDriver,
)
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import PromptResponseRagModule, VectorStoreRetrievalRagModule
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage
from griptape.memory import TaskMemory
from griptape.memory.task.storage import TextArtifactStorage
from griptape.structures import Agent
from griptape.tools import FileManager, TaskMemoryClient, WebScraper

vector_store_driver = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

agent = Agent(
    config=OpenAiStructureConfig(
        prompt_driver=OpenAiChatPromptDriver(model="gpt-4"),
    ),
    task_memory=TaskMemory(
        artifact_storages={
            TextArtifact: TextArtifactStorage(
                rag_engine=RagEngine(
                    retrieval_stage=RetrievalRagStage(
                        retrieval_modules=[
                            VectorStoreRetrievalRagModule(
                                vector_store_driver=vector_store_driver,
                                query_params={"namespace": "griptape", "count": 20},
                            )
                        ]
                    ),
                    response_stage=ResponseRagStage(
                        response_module=PromptResponseRagModule(prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"))
                    ),
                ),
                retrieval_rag_module_name="VectorStoreRetrievalRagModule",
                vector_store_driver=vector_store_driver,
            )
        }
    ),
    tools=[
        WebScraper(off_prompt=True),
        TaskMemoryClient(off_prompt=True, allowlist=["query"]),
        FileManager(off_prompt=True),
    ],
)

agent.run(
    "Use this page https://en.wikipedia.org/wiki/Elden_Ring to find how many copies of Elden Ring have been sold, and then save the result to a file."
)
