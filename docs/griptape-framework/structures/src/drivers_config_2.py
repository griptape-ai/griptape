import os

from griptape.configs import Defaults
from griptape.configs.drivers import AzureOpenAiDriversConfig
from griptape.structures import Agent

Defaults.drivers_config = AzureOpenAiDriversConfig(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_1"], api_key=os.environ["AZURE_OPENAI_API_KEY_1"]
)

agent = Agent()
