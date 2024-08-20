from griptape.configs import Defaults
from griptape.configs.drivers import GoogleDriversConfig
from griptape.structures import Agent

Defaults.drivers_config = GoogleDriversConfig()

agent = Agent()
