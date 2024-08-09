from griptape.artifacts import TextArtifact
from griptape.config import (
    OpenAiDriverConfig,
    config,
)
from griptape.drivers import (
    LocalVectorStoreDriver,
    OpenAiChatPromptDriver,
    OpenAiEmbeddingDriver,
)
from griptape.memory import TaskMemory
from griptape.memory.task.storage import TextArtifactStorage
from griptape.structures import Agent
from griptape.tools import FileManager, TaskMemoryClient, WebScraper

config.drivers = OpenAiDriverConfig(
    prompt=OpenAiChatPromptDriver(model="gpt-4"),
)

vector_store_driver = LocalVectorStoreDriver(embedding_driver=OpenAiEmbeddingDriver())

agent = Agent(
    task_memory=TaskMemory(
        artifact_storages={
            TextArtifact: TextArtifactStorage(
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
