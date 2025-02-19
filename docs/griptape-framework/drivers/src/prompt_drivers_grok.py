import os

from griptape.drivers.prompt.grok import GrokPromptDriver
from griptape.rules import Rule
from griptape.structures import Agent

agent = Agent(
    prompt_driver=GrokPromptDriver(model="grok-2-latest", api_key=os.environ["GROK_API_KEY"]),
    rules=[Rule("You are Grok, a chatbot inspired by the Hitchhikers Guide to the Galaxy.")],
)

agent.run("What is the meaning of life, the universe, and everything?")
