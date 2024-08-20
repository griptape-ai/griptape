import os

from griptape.config import config
from griptape.config.drivers import CohereDriversConfig
from griptape.structures import Agent

config.drivers_config = CohereDriversConfig(api_key=os.environ["COHERE_API_KEY"])

agent = Agent()
