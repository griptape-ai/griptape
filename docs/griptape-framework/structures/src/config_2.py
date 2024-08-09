import os

from griptape.config import AzureOpenAiStructureConfig
from griptape.structures import Agent

agent = Agent(
    config=AzureOpenAiStructureConfig(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_3"], api_key=os.environ["AZURE_OPENAI_API_KEY_3"]
    ).merge_config(
        {
            "image_query_driver": {
                "azure_deployment": "gpt-4o",
            },
        }
    ),
)
