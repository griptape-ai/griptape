from griptape.configs import Defaults
from griptape.configs.drivers import DriversConfig
from griptape.drivers.embedding.voyageai import VoyageAiEmbeddingDriver
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.structures import Agent
from griptape.tools import PromptSummaryTool, WebScraperTool

Defaults.drivers_config = DriversConfig(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4.1"),
    embedding_driver=VoyageAiEmbeddingDriver(),
)

Defaults.drivers_config = DriversConfig(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4.1"),
    embedding_driver=VoyageAiEmbeddingDriver(),
)

agent = Agent(
    tools=[WebScraperTool(off_prompt=True), PromptSummaryTool(off_prompt=False)],
)

agent.run("based on https://www.griptape.ai/, tell me what Griptape is")
