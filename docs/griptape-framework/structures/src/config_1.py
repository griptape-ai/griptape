from griptape.config import OpenAiDriverConfig, config
from griptape.structures import Agent

config.drivers = OpenAiDriverConfig()

agent = Agent()
