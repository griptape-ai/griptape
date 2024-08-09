import os

from griptape.config import AzureOpenAiDriverConfig, config
from griptape.structures import Agent

config.drivers = AzureOpenAiDriverConfig(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_3"], api_key=os.environ["AZURE_OPENAI_API_KEY_3"]
)

agent = Agent()
