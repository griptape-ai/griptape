import os

from griptape.config import CohereStructureConfig
from griptape.structures import Agent

agent = Agent(config=CohereStructureConfig(api_key=os.environ["COHERE_API_KEY"]))
