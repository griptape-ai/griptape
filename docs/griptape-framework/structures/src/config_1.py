from griptape.config import config
from griptape.config.drivers import OpenAiDriverConfig
from griptape.structures import Agent

config.drivers = OpenAiDriverConfig()

agent = Agent()
