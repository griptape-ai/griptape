from griptape.configs import Defaults
from griptape.configs.drivers import OpenAiDriversConfig
from griptape.structures import Agent

Defaults.drivers_config = OpenAiDriversConfig()

agent = Agent()
