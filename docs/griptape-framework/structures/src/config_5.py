from griptape.config import config
from griptape.config.drivers import AnthropicDriverConfig
from griptape.structures import Agent

config.drivers = AnthropicDriverConfig()

agent = Agent()
