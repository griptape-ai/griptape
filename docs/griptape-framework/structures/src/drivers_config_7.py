import os

from griptape.configs import config
from griptape.configs.drivers import DriversConfig
from griptape.drivers import AnthropicPromptDriver
from griptape.structures import Agent

config.drivers_config = DriversConfig(
    prompt_driver=AnthropicPromptDriver(
        model="claude-3-sonnet-20240229",
        api_key=os.environ["ANTHROPIC_API_KEY"],
    )
)


agent = Agent()
