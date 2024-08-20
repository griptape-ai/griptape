from griptape.configs import config
from griptape.configs.drivers import OpenAiDriversConfig
from griptape.structures import Agent

config.drivers_config = OpenAiDriversConfig()

agent = Agent()
