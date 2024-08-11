import os

from griptape.config import StructureConfig
from griptape.drivers import OpenAiChatPromptDriver
from griptape.rules import Rule
from griptape.structures import Agent

agent = Agent(
    config=StructureConfig(
        prompt_driver=OpenAiChatPromptDriver(
            api_key=os.environ["OPENAI_API_KEY"],
            temperature=0.1,
            model="gpt-4o",
            response_format="json_object",
            seed=42,
        )
    ),
    input="You will be provided with a description of a mood, and your task is to generate the CSS code for a color that matches it. Description: {{ args[0] }}",
    rules=[Rule(value='Write your output in json with a single key called "css_code".')],
)

agent.run("Blue sky at dusk.")
