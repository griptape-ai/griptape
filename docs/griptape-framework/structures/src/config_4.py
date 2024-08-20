from griptape.config import config
from griptape.config.drivers import GoogleDriversConfig
from griptape.structures import Agent

config.drivers_config = GoogleDriversConfig()

agent = Agent()
