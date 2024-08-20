import os

from griptape.configs import Defaults
from griptape.configs.drivers import CohereDriversConfig
from griptape.structures import Agent

Defaults.drivers_config = CohereDriversConfig(api_key=os.environ["COHERE_API_KEY"])

agent = Agent()
