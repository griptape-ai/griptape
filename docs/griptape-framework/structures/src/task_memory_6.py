from griptape.artifacts import TextArtifact
from griptape.config import config
from griptape.config.drivers import OpenAiDriversConfig
from griptape.drivers import (
    LocalVectorStoreDriver,
    OpenAiChatPromptDriver,
    OpenAiEmbeddingDriver,
)
from griptape.memory import TaskMemory
from griptape.memory.task.storage import TextArtifactStorage
from griptape.structures import Agent
from griptape.tools import FileManagerTool, QueryTool, WebScraperTool

config.drivers_config = OpenAiDriversConfig(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4"),
)

config.drivers_config = OpenAiDriversConfig(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4"),
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
        WebScraperTool(off_prompt=True),
        QueryTool(off_prompt=True),
        FileManagerTool(off_prompt=True),
    ],
)

agent.run(
    "Use this page https://en.wikipedia.org/wiki/Elden_Ring to find how many copies of Elden Ring have been sold, and then save the result to a file."
)
