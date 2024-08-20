from griptape.config import config
from griptape.config.drivers import OpenAiDriversConfig
from griptape.structures import Agent

config.drivers_config = OpenAiDriversConfig()

agent = Agent()
