from griptape.config import DriverConfig, config
from griptape.drivers import (
    OpenAiChatPromptDriver,
    VoyageAiEmbeddingDriver,
)
from griptape.structures import Agent
from griptape.tools import PromptSummaryClient, WebScraper

config.drivers = DriverConfig(
    prompt=OpenAiChatPromptDriver(model="gpt-4o"),
    embedding=VoyageAiEmbeddingDriver(),
)

agent = Agent(
    tools=[WebScraper(off_prompt=True), PromptSummaryClient(off_prompt=False)],
)

agent.run("based on https://www.griptape.ai/, tell me what Griptape is")
