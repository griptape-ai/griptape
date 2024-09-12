import os

from griptape.configs import Defaults
from griptape.configs.drivers import DriversConfig
from griptape.drivers import AnthropicPromptDriver, OpenAiEmbeddingDriver
from griptape.structures import Agent

Defaults.drivers_config = DriversConfig(
    prompt_driver=AnthropicPromptDriver(
        model="claude-3-sonnet-20240229",
        api_key=os.environ["ANTHROPIC_API_KEY"],
    ),
    embedding_driver=OpenAiEmbeddingDriver(),
)


agent = Agent()
