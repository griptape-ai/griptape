import os

from griptape.drivers import GooglePromptDriver
from griptape.structures import Agent

agent = Agent(
    prompt_driver=GooglePromptDriver(
        model="gemini-pro",
        api_key=os.environ["GOOGLE_API_KEY"],
    )
)

agent.run("Briefly explain how a computer works to a young child.")
