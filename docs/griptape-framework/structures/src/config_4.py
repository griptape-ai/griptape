from griptape.config import config
from griptape.config.drivers import GoogleDriverConfig
from griptape.structures import Agent

config.drivers = GoogleDriverConfig()

agent = Agent()
