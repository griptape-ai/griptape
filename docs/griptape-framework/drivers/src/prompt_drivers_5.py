import os

from griptape.drivers.prompt.openai import AzureOpenAiChatPromptDriver
from griptape.rules import Rule
from griptape.structures import Agent

agent = Agent(
    prompt_driver=AzureOpenAiChatPromptDriver(
        api_key=os.environ["AZURE_OPENAI_API_KEY_1"],
        model="gpt-4.1",
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_1"],
    ),
    rules=[
        Rule(
            value="You will be provided with text, and your task is to translate it into emojis. "
            "Do not use any regular text. Do your best with emojis only."
        )
    ],
)

agent.run("Artificial intelligence is a technology with great promise.")
