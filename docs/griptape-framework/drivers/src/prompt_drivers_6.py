import os

from griptape.config import StructureConfig
from griptape.drivers import CoherePromptDriver
from griptape.structures import Agent

agent = Agent(
    config=StructureConfig(
        prompt_driver=CoherePromptDriver(
            model="command-r",
            api_key=os.environ["COHERE_API_KEY"],
        )
    )
)

agent.run('What is the sentiment of this review? Review: "I really enjoyed this movie!"')
