import os

from griptape.config import config
from griptape.config.drivers import DriverConfig
from griptape.drivers import AnthropicPromptDriver
from griptape.structures import Agent

config.driver_config = DriverConfig(
    prompt_driver=AnthropicPromptDriver(
        model="claude-3-sonnet-20240229",
        api_key=os.environ["ANTHROPIC_API_KEY"],
    )
)


agent = Agent()
