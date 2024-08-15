from griptape.artifacts import TextArtifact
from griptape.config import config
from griptape.config.drivers import OpenAiDriverConfig
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
from griptape.tools import FileManagerTool, TaskMemoryTool, WebScraperTool

config.drivers = OpenAiDriverConfig(
    prompt=OpenAiChatPromptDriver(model="gpt-4"),
)

vector_store_driver = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

agent = Agent(
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
                        response_modules=[PromptResponseRagModule(prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"))]
                    ),
                ),
                retrieval_rag_module_name="VectorStoreRetrievalRagModule",
                vector_store_driver=vector_store_driver,
            )
        }
    ),
    tools=[
        WebScraperTool(off_prompt=True),
        TaskMemoryTool(off_prompt=True, allowlist=["query"]),
        FileManagerTool(off_prompt=True),
    ],
)

agent.run(
    "Use this page https://en.wikipedia.org/wiki/Elden_Ring to find how many copies of Elden Ring have been sold, and then save the result to a file."
)
