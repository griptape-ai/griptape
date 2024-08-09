import os

from griptape.config import DriverConfig, config
from griptape.drivers import AnthropicPromptDriver
from griptape.structures import Agent

config.drivers = DriverConfig(
    prompt=AnthropicPromptDriver(
        model="claude-3-sonnet-20240229",
        api_key=os.environ["ANTHROPIC_API_KEY"],
    )
)


agent = Agent()
