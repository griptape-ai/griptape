from griptape.config import StructureConfig
from griptape.drivers import (
    OpenAiChatPromptDriver,
    VoyageAiEmbeddingDriver,
)
from griptape.structures import Agent
from griptape.tools import TaskMemoryClient, WebScraper

agent = Agent(
    tools=[WebScraper(off_prompt=True), TaskMemoryClient(off_prompt=False)],
    config=StructureConfig(
        prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"),
        embedding_driver=VoyageAiEmbeddingDriver(),
    ),
)

agent.run("based on https://www.griptape.ai/, tell me what Griptape is")
