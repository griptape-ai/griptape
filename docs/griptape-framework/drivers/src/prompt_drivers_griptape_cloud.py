import os

from griptape.drivers.prompt.griptape_cloud import GriptapeCloudPromptDriver
from griptape.rules import Rule
from griptape.structures import Agent

agent = Agent(
    prompt_driver=GriptapeCloudPromptDriver(
        api_key=os.environ["GT_CLOUD_API_KEY"],
    ),
    rules=[
        Rule(
            "You will be provided with a product description and seed words, and your task is to generate product names.",
        ),
    ],
)

agent.run("Product description: A home milkshake maker. Seed words: fast, healthy, compact.")
