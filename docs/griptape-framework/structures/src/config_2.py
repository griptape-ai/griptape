import os

from griptape.config import config
from griptape.config.drivers import AzureOpenAiDriversConfig
from griptape.structures import Agent

config.drivers_config = AzureOpenAiDriversConfig(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_3"], api_key=os.environ["AZURE_OPENAI_API_KEY_3"]
)

agent = Agent()
