from griptape.configs import config
from griptape.configs.drivers import AnthropicDriversConfig
from griptape.structures import Agent

config.drivers_config = AnthropicDriversConfig()

agent = Agent()
