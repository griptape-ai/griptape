import os

from griptape.drivers.prompt.google import GooglePromptDriver
from griptape.structures import Agent

agent = Agent(
    prompt_driver=GooglePromptDriver(
        model="gemini-2.0-flash",
        api_key=os.environ["GOOGLE_API_KEY"],
    )
)

agent.run("Briefly explain how a computer works to a young child.")
