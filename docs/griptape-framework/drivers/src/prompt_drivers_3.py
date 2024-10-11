import os

import schema

from griptape.drivers import OpenAiChatPromptDriver
from griptape.structures import Agent

agent = Agent(
    prompt_driver=OpenAiChatPromptDriver(
        api_key=os.environ["OPENAI_API_KEY"],
        model="gpt-4o-2024-08-06",
        temperature=0.1,
        seed=42,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "strict": True,
                "name": "Output",
                "schema": schema.Schema({"css_code": str, "relevant_emojies": [str]}).json_schema("Output Schema"),
            },
        },
    ),
    input="You will be provided with a description of a mood, and your task is to generate the CSS color code for a color that matches it. Description: {{ args[0] }}",
)

agent.run("Blue sky at dusk.")
