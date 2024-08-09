import os

from griptape.config import StructureConfig
from griptape.drivers import AnthropicPromptDriver
from griptape.structures import Agent

agent = Agent(
    config=StructureConfig(
        prompt_driver=AnthropicPromptDriver(
            model="claude-3-sonnet-20240229",
            api_key=os.environ["ANTHROPIC_API_KEY"],
        )
    ),
)
