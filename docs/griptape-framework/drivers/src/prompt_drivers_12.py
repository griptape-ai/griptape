import os

from griptape.config import StructureConfig
from griptape.drivers import HuggingFaceHubPromptDriver
from griptape.structures import Agent

agent = Agent(
    config=StructureConfig(
        prompt_driver=HuggingFaceHubPromptDriver(
            model="http://127.0.0.1:8080",
            api_token=os.environ["HUGGINGFACE_HUB_ACCESS_TOKEN"],
        ),
    ),
)

agent.run("Write the code for a snake game.")
