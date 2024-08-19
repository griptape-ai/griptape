import os

from griptape.config import config
from griptape.config.drivers import CohereDriverConfig
from griptape.structures import Agent

config.driver_config = CohereDriverConfig(api_key=os.environ["COHERE_API_KEY"])

agent = Agent()
