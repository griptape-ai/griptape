from griptape.configs import config
from griptape.configs.drivers import GoogleDriversConfig
from griptape.structures import Agent

config.drivers_config = GoogleDriversConfig()

agent = Agent()
