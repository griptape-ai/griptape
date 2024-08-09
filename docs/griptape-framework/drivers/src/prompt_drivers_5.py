import os

from griptape.config import StructureConfig
from griptape.drivers import AzureOpenAiChatPromptDriver
from griptape.rules import Rule
from griptape.structures import Agent

agent = Agent(
    config=StructureConfig(
        prompt_driver=AzureOpenAiChatPromptDriver(
            api_key=os.environ["AZURE_OPENAI_API_KEY_1"],
            model="gpt-3.5-turbo",
            azure_deployment=os.environ["AZURE_OPENAI_35_TURBO_DEPLOYMENT_ID"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_1"],
        )
    ),
    rules=[
        Rule(
            value="You will be provided with text, and your task is to translate it into emojis. "
            "Do not use any regular text. Do your best with emojis only."
        )
    ],
)

agent.run("Artificial intelligence is a technology with great promise.")
