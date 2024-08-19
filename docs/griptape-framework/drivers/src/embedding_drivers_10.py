from griptape.config import config
from griptape.config.drivers import DriverConfig
from griptape.drivers import (
    OpenAiChatPromptDriver,
    VoyageAiEmbeddingDriver,
)
from griptape.structures import Agent
from griptape.tools import PromptSummaryTool, WebScraperTool

config.driver_config = DriverConfig(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"),
    embedding_driver=VoyageAiEmbeddingDriver(),
)

config.driver_config = DriverConfig(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"),
    embedding_driver=VoyageAiEmbeddingDriver(),
)

agent = Agent(
    tools=[WebScraperTool(off_prompt=True), PromptSummaryTool(off_prompt=False)],
)

agent.run("based on https://www.griptape.ai/, tell me what Griptape is")
