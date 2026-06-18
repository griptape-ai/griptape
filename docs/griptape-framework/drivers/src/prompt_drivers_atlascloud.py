import os

from griptape.drivers.prompt.atlascloud import AtlasCloudPromptDriver
from griptape.structures import Agent

agent = Agent(
    prompt_driver=AtlasCloudPromptDriver(
        model="deepseek-ai/deepseek-v4-pro",
        api_key=os.environ["ATLASCLOUD_API_KEY"],
    ),
)

agent.run("What are the benefits of using a unified AI API platform?")
