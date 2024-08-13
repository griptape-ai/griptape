import os

from griptape.config import CohereDriverConfig, config
from griptape.structures import Agent

config.drivers = CohereDriverConfig(api_key=os.environ["COHERE_API_KEY"])

agent = Agent()
