import os

from griptape.drivers import OpenAiChatPromptDriver
from griptape.structures import Agent

agent = Agent(
    prompt_driver=OpenAiChatPromptDriver(
        api_key=os.environ["OPENAI_API_KEY"],
        model="gpt-4o-2024-08-06",
        temperature=0.1,
        seed=42,
    ),
    input="You will be provided with a description of a mood, and your task is to generate the CSS color code for a color that matches it. Description: {{ args[0] }}",
)

agent.run("Blue sky at dusk.")
