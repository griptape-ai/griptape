from griptape.config import config
from griptape.config.drivers import OpenAiDriverConfig
from griptape.structures import Agent

config.driver_config = OpenAiDriverConfig()

agent = Agent()
