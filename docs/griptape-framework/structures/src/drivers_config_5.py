from griptape.configs import Defaults
from griptape.configs.drivers import AnthropicDriversConfig
from griptape.structures import Agent

Defaults.drivers_config = AnthropicDriversConfig()

agent = Agent()
