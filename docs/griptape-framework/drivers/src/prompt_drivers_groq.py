import os

from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.structures import Agent

agent = Agent(
    prompt_driver=OpenAiChatPromptDriver(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile",
    ),
)

agent.run("Hello")
